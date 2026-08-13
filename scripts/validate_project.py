#!/usr/bin/env python3
# 做什么：校验项目级 skill 结构、来源映射、触发边界和禁止的旧工具依赖。
# 怎么运行：python3 scripts/validate_project.py
# 需要什么：Python 3；只读扫描当前项目，发现问题时非零退出。

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".codex" / "skills"
LOCK = ROOT / "vendor" / "sources.lock.json"
REQUIRED = [
    "## When to Use This Skill",
    "## Not For / Boundaries",
    "## Quick Reference",
    "## Examples",
    "## Maintenance",
]
FORBIDDEN = [
    "mcp__codex__",
    "mcp__manual_review__",
    "mcp__zotero__",
    "mcp__obsidian-vault__",
    "allowed-tools: Agent",
]


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+)", text)
    return match.group(1).strip() if match else None


def main() -> int:
    errors: list[str] = []
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in lock["sources"]}
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"缺少 SKILL.md：{skill_dir}")
            continue
        text = skill_file.read_text(encoding="utf-8")
        name = frontmatter_value(text, "name")
        if name != skill_dir.name or not re.fullmatch(r"[a-z][a-z0-9-]*", name or ""):
            errors.append(f"skill 名称不匹配：{skill_dir} -> {name}")
        for heading in REQUIRED:
            if heading not in text:
                errors.append(f"{skill_dir.name} 缺少章节：{heading}")
        if text.count("### Example ") < 3:
            errors.append(f"{skill_dir.name} 缺少 3 个可复现实例")
        for filename in [
            "VERSION",
            "CHANGELOG.md",
            "references/index.md",
            "references/source-map.md",
            "references/pressure-tests.md",
        ]:
            if not (skill_dir / filename).is_file():
                errors.append(f"{skill_dir.name} 缺少 {filename}")
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"{skill_dir.name} 含禁止的不可用依赖：{token}")
        source_map = skill_dir / "references" / "source-map.md"
        if source_map.is_file() and skill_dir.name != "vibe-mathing-router":
            mapped = source_map.read_text(encoding="utf-8")
            if not any(source_id in mapped for source_id in source_ids):
                errors.append(f"{skill_dir.name} 未映射 lockfile 来源")

    expected = {
        "vibe-mathing-router", "math-discovery", "math-derivation",
        "math-computation", "math-proof", "math-formalization",
    }
    actual = {path.name for path in skill_dirs}
    if actual != expected:
        errors.append(f"active skill 集合漂移：期望 {sorted(expected)}，实际 {sorted(actual)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"项目校验通过：{len(skill_dirs)} 个 active skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
