"""可恢复运行状态机、预算、超时与有界子进程执行。"""

from __future__ import annotations

import hashlib
import json
import os
import resource
import signal
import subprocess
import tempfile
import fcntl
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


TERMINAL_STATES = {"accepted", "rejected", "blocked", "failed", "cancelled"}
TRANSITIONS = {
    "planned": {"routed", "cancelled"},
    "routed": {"running", "cancelled"},
    "running": {"candidate_ready", "blocked", "failed", "cancelled"},
    "candidate_ready": {"verifying", "blocked", "failed", "cancelled"},
    "verifying": {"accepted", "rejected", "blocked", "failed", "cancelled"},
}
DEFAULT_BUDGETS = {
    "max_transitions": 16,
    "max_retries": 2,
    "timeout_seconds": 30,
    "max_output_bytes": 1_048_576,
}


class RuntimeErrorBase(RuntimeError):
    """运行状态或预算契约失败。"""


class InjectedInterruption(RuntimeErrorBase):
    """测试用可恢复中断，不改变真实业务逻辑。"""


def _validate_state(project_root: Path, state: dict[str, Any]) -> None:
    schema_path = project_root / "research" / "schema" / "run-state.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeErrorBase(f"无法读取运行状态 schema：{schema_path}") from exc
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state),
        key=lambda item: list(item.path),
    )
    if errors:
        raise RuntimeErrorBase(f"运行状态 schema 无效：{errors[0].message}")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_run_id(problem_id: str, adapter: str) -> str:
    value = hashlib.sha256(f"{problem_id}\0{adapter}\0v1".encode()).hexdigest()[:20]
    return f"run:{value}"


def run_path(project_root: Path, run_id: str) -> Path:
    safe_id = run_id.removeprefix("run:")
    if not safe_id or not all(character in "0123456789abcdef" for character in safe_id):
        raise RuntimeErrorBase("run_id 格式无效")
    return project_root / "research" / "runs" / safe_id / "run.json"


@contextmanager
def locked_run(project_root: Path, run_id: str) -> Any:
    """序列化同一 run 的所有副作用，避免并发状态与 artifact 竞争。"""
    path = run_path(project_root, run_id).with_name("run.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def _write_atomic(path: Path, payload: dict[str, Any]) -> None:
    project_root = path.parents[3]
    _validate_state(project_root, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    try:
        with temporary.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def create_run(
    project_root: Path,
    problem_id: str,
    adapter: str,
    budgets: dict[str, int] | None = None,
) -> dict[str, Any]:
    run_id = stable_run_id(problem_id, adapter)
    path = run_path(project_root, run_id)
    if path.is_file():
        return load_run(project_root, run_id)
    effective = {**DEFAULT_BUDGETS, **(budgets or {})}
    if any(not isinstance(value, int) or value <= 0 for value in effective.values()):
        raise RuntimeErrorBase("所有运行预算必须是正整数")
    created = now()
    state = {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "problem_id": problem_id,
        "adapter": adapter,
        "status": "planned",
        "transition_count": 0,
        "retry_count": 0,
        "budgets": effective,
        "checkpoints": [{"status": "planned", "at": created}],
        "last_error": None,
        "created_at": created,
        "updated_at": created,
    }
    _write_atomic(path, state)
    return state


def load_run(project_root: Path, run_id: str) -> dict[str, Any]:
    path = run_path(project_root, run_id)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeErrorBase(f"无法读取运行状态：{run_id}") from exc
    _validate_state(project_root, state)
    if state.get("run_id") != run_id:
        raise RuntimeErrorBase("运行状态身份或 schema_version 漂移")
    return state


def transition(project_root: Path, state: dict[str, Any], target: str) -> dict[str, Any]:
    current = state.get("status")
    if current in TERMINAL_STATES or target not in TRANSITIONS.get(current, set()):
        raise RuntimeErrorBase(f"非法运行状态转换：{current} -> {target}")
    count = state["transition_count"] + 1
    if count > state["budgets"]["max_transitions"]:
        raise RuntimeErrorBase("运行转换预算耗尽")
    changed = {**state, "status": target, "transition_count": count, "updated_at": now()}
    changed["checkpoints"] = [*state["checkpoints"], {"status": target, "at": changed["updated_at"]}]
    _write_atomic(run_path(project_root, state["run_id"]), changed)
    return changed


def execute_bounded(
    argv: list[str], *, cwd: Path, timeout_seconds: int, max_output_bytes: int
) -> dict[str, Any]:
    if not argv or any(not isinstance(item, str) or not item for item in argv):
        raise RuntimeErrorBase("子进程 argv 无效")
    def limit_output() -> None:
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_output_bytes + 1, max_output_bytes + 1))

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True,
            preexec_fn=limit_output,
        )
        try:
            return_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            raise RuntimeErrorBase(f"子进程超时：{timeout_seconds}s") from exc
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read(max_output_bytes + 1)
        stderr = stderr_file.read(max_output_bytes + 1)
    if len(stdout) > max_output_bytes or len(stderr) > max_output_bytes or return_code < 0:
        raise RuntimeErrorBase("子进程输出超过预算或被资源限制终止")
    return {
        "argv": argv,
        "exit_code": return_code,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


def record_retry(project_root: Path, state: dict[str, Any], error: str) -> dict[str, Any]:
    retries = state["retry_count"] + 1
    if retries > state["budgets"]["max_retries"]:
        raise RuntimeErrorBase("运行重试预算耗尽")
    changed = {**state, "retry_count": retries, "last_error": error, "updated_at": now()}
    _write_atomic(run_path(project_root, state["run_id"]), changed)
    return changed


def cancel_run(project_root: Path, run_id: str) -> dict[str, Any]:
    """在 run 互斥锁内执行显式取消；终态取消保持幂等。"""
    with locked_run(project_root, run_id):
        state = load_run(project_root, run_id)
        if state["status"] == "cancelled":
            return state
        current = state["status"]
        if current in TERMINAL_STATES or "cancelled" not in TRANSITIONS.get(current, set()):
            raise RuntimeErrorBase(f"非法运行状态转换：{current} -> cancelled")
        cancelled_at = now()
        changed = {
            **state,
            "status": "cancelled",
            "updated_at": cancelled_at,
            "last_error": "用户或监管器显式取消",
            "checkpoints": [
                *state["checkpoints"],
                {"status": "cancelled", "at": cancelled_at},
            ],
        }
        _write_atomic(run_path(project_root, run_id), changed)
        return changed
