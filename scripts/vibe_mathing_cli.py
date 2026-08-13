#!/usr/bin/env python3
# 做什么：提供 run、resume、verify、status 的统一 Vibe Mathing 单机入口。
# 怎么运行：python3 scripts/vibe_mathing_cli.py <command> [options]
# 需要什么：Python 3、项目依赖与已注册 adapter；所有写入由 ResearchStore 完成。

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vibe_mathing.pipeline import SYMPY_ADAPTER, run_sympy_pipeline
from vibe_mathing.runtime import cancel_run, load_run
from vibe_mathing.store import ResearchStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Vibe Mathing 可信研究闭环")
    parser.add_argument("--project-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--problem-id", required=True)
    run_parser.add_argument("--adapter", default=SYMPY_ADAPTER, choices=[SYMPY_ADAPTER])
    run_parser.add_argument("--fail-after", choices=["candidate_ready", "result_written"])
    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--run-id", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--run-id", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--run-id", required=True)
    cancel_parser = subparsers.add_parser("cancel")
    cancel_parser.add_argument("--run-id", required=True)
    register_parser = subparsers.add_parser("register-problem")
    register_parser.add_argument("--file", required=True)
    args = parser.parse_args()
    root = Path(args.project_root).resolve()

    if args.command == "register-problem":
        source = Path(args.file).resolve()
        try:
            source.relative_to(root)
        except ValueError:
            parser.error("Problem 文件必须位于 project root 内")
        try:
            problem = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"无法读取 Problem JSON：{exc}")
        created = ResearchStore(root).upsert("problems", problem)
        print(json.dumps({"problem_id": problem.get("problem_id"), "created": created}, ensure_ascii=False))
        return 0
    if args.command == "run":
        state = run_sympy_pipeline(root, args.problem_id, fail_after=args.fail_after)
    elif args.command == "resume":
        current = load_run(root, args.run_id)
        if current["adapter"] != SYMPY_ADAPTER:
            parser.error(f"不支持恢复 adapter={current['adapter']}")
        state = run_sympy_pipeline(root, current["problem_id"])
    elif args.command == "status":
        state = load_run(root, args.run_id)
    elif args.command == "verify":
        state = load_run(root, args.run_id)
        expected = f"result:{args.run_id.removeprefix('run:')}"
        solutions = ResearchStore(root).rebuild_solution_view()
        accepted = state["status"] == "accepted"
        if (expected in solutions) is not accepted:
            raise SystemExit("验证失败：run 终态与 Solution View 不一致")
    else:
        state = cancel_run(root, args.run_id)

    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
