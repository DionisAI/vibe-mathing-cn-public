#!/usr/bin/env python3
# 做什么：按 vendor/sources.lock.json 同步或检查 Git 上游、本机研究归档镜像和审计快照。
# 怎么运行：python3 scripts/sync_supply_chain.py [--check]
# 需要什么：Python 3、Git、rsync；Git 上游同步需要网络，本机镜像不需要网络。

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "vendor" / "sources.lock.json"


def run(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"命令失败（{result.returncode}）：{' '.join(args)}\n{detail}")
    return result.stdout.strip()


def load_sources() -> list[dict[str, object]]:
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    return list(data["sources"])


def repo_path(source: dict[str, object]) -> Path:
    return ROOT / str(source["path"])


def ensure_clean(path: Path) -> None:
    dirty = run(["git", "status", "--porcelain"], cwd=path)
    if dirty:
        raise RuntimeError(f"供应链缓存存在本地改动，拒绝覆盖：{path}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded(relative: Path, patterns: list[str]) -> bool:
    return any(
        pattern in relative.parts
        or fnmatch.fnmatch(relative.name, pattern)
        or fnmatch.fnmatch(relative.as_posix(), pattern)
        for pattern in patterns
    )


def tree_inventory(path: Path, exclusions: list[str]) -> dict[str, object]:
    if not path.is_dir():
        raise RuntimeError(f"目录不存在：{path}")
    root = path.resolve()
    digest = hashlib.sha256()
    regular_files = 0
    directories = 0
    symlinks = 0
    skill_files = 0
    total_bytes = 0

    candidates = sorted(
        (
            candidate
            for candidate in path.rglob("*")
            if not is_excluded(candidate.relative_to(path), exclusions)
        ),
        key=lambda candidate: candidate.relative_to(path).as_posix(),
    )
    for candidate in candidates:
        relative = candidate.relative_to(path)
        relative_text = relative.as_posix()
        if candidate.is_symlink():
            target = candidate.readlink().as_posix()
            try:
                candidate.resolve(strict=True).relative_to(root)
            except (OSError, ValueError) as exc:
                raise RuntimeError(
                    f"供应链镜像包含失效或越界符号链接：{candidate} -> {target}"
                ) from exc
            digest.update(f"L\0{relative_text}\0{target}\n".encode())
            symlinks += 1
        elif candidate.is_dir():
            digest.update(f"D\0{relative_text}\n".encode())
            directories += 1
        elif candidate.is_file():
            size = candidate.stat().st_size
            file_digest = sha256(candidate)
            digest.update(
                f"F\0{relative_text}\0{size}\0{file_digest}\n".encode()
            )
            regular_files += 1
            total_bytes += size
            if candidate.name == "SKILL.md":
                skill_files += 1

    return {
        "regular_files": regular_files,
        "directories": directories,
        "symlinks": symlinks,
        "skill_files": skill_files,
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def local_source_path(source: dict[str, object]) -> Path:
    return Path(str(source["source_path"])).expanduser().resolve()


def sync_local_mirror(source: dict[str, object]) -> None:
    origin = local_source_path(source)
    target = repo_path(source)
    if not origin.is_dir():
        raise RuntimeError(f"本机归档不存在：{origin}")
    target.mkdir(parents=True, exist_ok=True)
    exclusions = [str(item) for item in source.get("exclusions", [])]
    args = ["rsync", "-a", "--delete", "--delete-excluded"]
    for pattern in exclusions:
        suffix = "/" if pattern in {".git", "__pycache__"} else ""
        args.append(f"--exclude={pattern}{suffix}")
    args.extend([f"{origin}/", f"{target}/"])
    run(args)


def check_local_mirror(source: dict[str, object]) -> list[str]:
    origin = local_source_path(source)
    target = repo_path(source)
    if not origin.is_dir():
        return [f"缺少本机归档：{origin}"]
    if not target.is_dir():
        return [f"缺少本机归档镜像：{target}"]

    exclusions = [str(item) for item in source.get("exclusions", [])]
    try:
        origin_inventory = tree_inventory(origin, exclusions)
        target_inventory = tree_inventory(target, exclusions)
    except (OSError, RuntimeError) as exc:
        return [str(exc)]

    errors: list[str] = []
    if origin_inventory != target_inventory:
        errors.append(f"本机归档镜像与来源不一致：{target}")
    expected = source.get("inventory")
    if not isinstance(expected, dict):
        errors.append(f"本机归档缺少锁定 inventory：{source['id']}")
    elif target_inventory != expected:
        errors.append(
            f"本机归档 inventory 漂移：{source['id']} 实际 "
            f"{json.dumps(target_inventory, ensure_ascii=False, sort_keys=True)}"
        )
    return errors


def sync_git(source: dict[str, object]) -> None:
    path = repo_path(source)
    url = str(source["url"])
    branch = str(source["branch"])
    commit = str(source["commit"])
    sparse_paths = [str(item) for item in source.get("sparse_paths", [])]

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        run([
            "git", "clone", "--depth", "1", "--filter=blob:none",
            "--branch", branch, url, str(path),
        ])
    ensure_clean(path)

    actual_url = run(["git", "remote", "get-url", "origin"], cwd=path)
    if actual_url != url:
        raise RuntimeError(f"远端漂移：{path} 期望 {url}，实际 {actual_url}")

    actual_commit = run(["git", "rev-parse", "HEAD"], cwd=path)
    if actual_commit != commit:
        run(["git", "fetch", "--depth", "1", "origin", commit], cwd=path)
        run(["git", "switch", "--detach", commit], cwd=path)

    if sparse_paths:
        run(["git", "sparse-checkout", "init", "--cone"], cwd=path)
        run(["git", "sparse-checkout", "set", *sparse_paths], cwd=path)


def check_git(source: dict[str, object]) -> list[str]:
    errors: list[str] = []
    path = repo_path(source)
    if not path.is_dir():
        return [f"缺少供应链仓库：{path}"]
    try:
        ensure_clean(path)
        actual_url = run(["git", "remote", "get-url", "origin"], cwd=path)
        actual_commit = run(["git", "rev-parse", "HEAD"], cwd=path)
    except RuntimeError as exc:
        return [str(exc)]
    if actual_url != source["url"]:
        errors.append(f"远端漂移：{path}")
    if actual_commit != source["commit"]:
        errors.append(f"commit 漂移：{path} 实际 {actual_commit}")
    for relative in source.get("sparse_paths", []):
        if not (path / str(relative)).exists():
            errors.append(f"缺少 sparse path：{path / str(relative)}")
    license_path = source.get("license_path")
    if license_path:
        candidate = path / str(license_path)
        if not candidate.is_file():
            errors.append(f"缺少许可证：{candidate}")
        elif sha256(candidate) != source.get("license_sha256"):
            errors.append(f"许可证哈希漂移：{candidate}")
    return errors


def check_snapshot(source: dict[str, object]) -> list[str]:
    declared = Path(str(source["source_path"]))
    path = declared if declared.is_absolute() else ROOT / declared
    if not path.exists():
        return [f"缺少本机 snapshot：{path}"]
    errors: list[str] = []
    files = source.get("files")
    if isinstance(files, dict):
        for relative, expected in files.items():
            candidate = path / str(relative) if path.is_dir() else path
            if not candidate.is_file():
                errors.append(f"缺少 snapshot 文件：{candidate}")
            elif sha256(candidate) != expected:
                errors.append(f"snapshot 哈希漂移：{candidate}")
    elif source.get("sha256"):
        if not path.is_file() or sha256(path) != source["sha256"]:
            errors.append(f"snapshot 哈希漂移：{path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="同步或检查 Vibe Mathing 供应链")
    parser.add_argument("--check", action="store_true", help="只读检查，不访问或更新远端")
    args = parser.parse_args()

    errors: list[str] = []
    for source in load_sources():
        source_id = str(source["id"])
        try:
            if source["kind"] == "git":
                if not args.check:
                    sync_git(source)
                errors.extend(check_git(source))
            elif source["kind"] == "local-mirror":
                if not args.check:
                    sync_local_mirror(source)
                errors.extend(check_local_mirror(source))
            else:
                errors.extend(check_snapshot(source))
            print(f"{'CHECK' if args.check else 'SYNC'} {source_id}")
        except RuntimeError as exc:
            errors.append(f"{source_id}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("供应链检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
