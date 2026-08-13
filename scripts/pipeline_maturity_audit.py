#!/usr/bin/env python3
# 做什么：现场运行生产闭环 required capabilities，并从退出码派生 0–100 成熟度。
# 怎么运行：python3 scripts/pipeline_maturity_audit.py [--strict] [--output path]
# 需要什么：Python 3、项目依赖；严格模式要求 Lean/Mathlib fixture 可真实构建。

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = [
    ("trusted-evidence", 10, ["python3", "scripts/test_trusted_evidence.py"], 60),
    ("evidence-attacks", 10, ["python3", "scripts/test_evidence_attacks.py"], 60),
    ("research-space", 10, ["python3", "scripts/test_research_spaces.py"], 60),
    ("atomic-store", 15, ["python3", "scripts/test_research_store.py"], 60),
    ("bounded-runtime", 15, ["python3", "scripts/test_vibe_mathing_runtime.py"], 60),
    ("sympy-e2e", 15, ["python3", "scripts/test_vibe_mathing_pipeline.py"], 120),
    ("lean-e2e", 15, ["python3", "scripts/test_lean_pipeline.py"], 900),
    ("portable-quality-gate", 10, ["make", "check"], 300),
]


def run_capability(
    capability_id: str, weight: int, argv: list[str], timeout: int
) -> dict[str, Any]:
    started = time.monotonic()
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ.get('PATH', '')}"}
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = completed.returncode == 0
        exit_code: int | None = completed.returncode
        output = (completed.stdout + completed.stderr)[-4000:]
    except subprocess.TimeoutExpired as exc:
        passed = False
        exit_code = None
        output = f"TIMEOUT after {timeout}s: {exc}"
    duration = time.monotonic() - started
    return {
        "id": capability_id,
        "weight": weight,
        "status": "PASS" if passed else "FAIL",
        "argv": argv,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 3),
        "output_tail": output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 Vibe Mathing 单机生产闭环成熟度")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    results = [run_capability(*item) for item in CAPABILITIES]
    score = sum(item["weight"] for item in results if item["status"] == "PASS")
    maximum = sum(item["weight"] for item in results)
    payload = {
        "schema_version": "1.0.0",
        "scope": "single-host-single-agent-trusted-research-loop",
        "audited_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "score": score,
        "maximum": maximum,
        "readiness": f"{score}/{maximum}",
        "status": "PASS" if score == maximum else "FAIL",
        "capabilities": results,
        "excluded": [
            "distributed high availability",
            "external reviewer attestation issuance",
            "guaranteed solution of arbitrary open problems",
        ],
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    print(encoded, end="")
    if args.output:
        output = (ROOT / args.output).resolve()
        output.relative_to(ROOT)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    if args.strict and score != maximum:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
