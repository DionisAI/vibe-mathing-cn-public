#!/usr/bin/env python3
"""Validate that the current Git tree is safe for the public repository."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"^governance/tasks/001[0-5]-millennium-"),
    re.compile(r"^governance/tasks/millennium-goals/"),
    re.compile(r"^governance/verification/ledger/"),
    re.compile(r"^research/artifacts/(?!README\.md$)"),
    re.compile(r"^research/runs/"),
    re.compile(r"(^|/)RECOVERY_MANIFEST\.json$"),
)
FORBIDDEN_SUFFIXES = (
    ".olean",
    ".pyc",
    ".log",
    ".pdf",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".bin",
    ".zip",
    ".tar",
    ".tgz",
    ".gz",
    ".zst",
    ".7z",
    ".safetensors",
)

# Build sensitive literals in pieces so the validator does not flag its own source.
PRIVATE_REPOSITORY_NAME = b"vibe-mathing-cn-" + b"internal"
USER_PROJECT_PATH = re.compile(b"/" + b"home" + rb"/[^/]+/\.projects/vibe-mathing-cn(?:/|\b)")
WSL_UNC_PATH = re.compile(rb"\\\\wsl(?:\.localhost|\$)\\", re.IGNORECASE)
PRIVATE_IPV4 = re.compile(
    rb"(?<![A-Za-z0-9.-])(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})(?![A-Za-z0-9.-])"
)
CREDENTIAL_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    "bearer_token": re.compile(rb"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    "github_token": re.compile(rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    "openai_like_key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def forbidden_path(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(FORBIDDEN_SUFFIXES) or any(pattern.search(path) for pattern in FORBIDDEN_PATH_PATTERNS)


def content_findings(data: bytes) -> list[str]:
    findings: list[str] = []
    if PRIVATE_REPOSITORY_NAME in data:
        findings.append("private_repository_name")
    if USER_PROJECT_PATH.search(data):
        findings.append("absolute_user_project_path")
    if WSL_UNC_PATH.search(data):
        findings.append("wsl_unc_path")
    if PRIVATE_IPV4.search(data):
        findings.append("private_ipv4")
    for name, pattern in CREDENTIAL_PATTERNS.items():
        if pattern.search(data):
            findings.append(name)
    return findings


def validate(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not (root / ".git").exists():
        return [{"code": "not_git_repository", "path": str(root), "message": "public root is not a Git repository"}]

    origin = run_git(root, "remote", "get-url", "origin", check=False)
    if origin.returncode == 0 and not origin.stdout.decode().strip().rstrip("/").endswith("vibe-mathing-cn-public.git"):
        issues.append({"code": "wrong_public_origin", "path": "origin", "message": "origin is not the public repository"})
    remotes = run_git(root, "remote").stdout.decode().splitlines()
    for remote in remotes:
        url = run_git(root, "remote", "get-url", remote, check=False).stdout
        if PRIVATE_REPOSITORY_NAME in url:
            issues.append({"code": "private_remote_configured", "path": remote, "message": "public repository has a private remote"})

    tracked = [item.decode("utf-8", "surrogateescape") for item in run_git(root, "ls-files", "-z").stdout.split(b"\0") if item]
    for relative in tracked:
        if forbidden_path(relative):
            issues.append({"code": "forbidden_public_path", "path": relative, "message": "path is not publishable"})
            continue
        path = root / relative
        if path.is_symlink():
            issues.append({"code": "public_symlink", "path": relative, "message": "tracked symlinks are not allowed"})
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            issues.append({"code": "unreadable_tracked_file", "path": relative, "message": str(error)})
            continue
        if b"\0" in data[:8192]:
            issues.append({"code": "unclassified_binary", "path": relative, "message": "binary tracked file is not allowlisted"})
            continue
        for finding in content_findings(data):
            issues.append({"code": finding, "path": relative, "message": "sensitive content pattern found"})
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    issues = validate(Path(args.project_root).resolve())
    payload = {"decision": "PASS" if not issues else "BLOCK", "issue_count": len(issues), "issues": issues}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Public repository boundary: {payload['decision']}")
        for issue in issues:
            print(f"- {issue['code']} {issue['path']}: {issue['message']}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
