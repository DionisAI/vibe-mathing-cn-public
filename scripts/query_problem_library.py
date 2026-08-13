#!/usr/bin/env python3
# 按来源、状态、分类或全文关键字查询本地 JSONL 问题库。
# 运行：python3 scripts/query_problem_library.py --text riemann --limit 10 [--json]
# 依赖：Python 3 与已生成的 problem-library/records/problems.jsonl。

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
RECORDS_PATH = ROOT / "problem-library" / "records" / "problems.jsonl"


def records() -> Iterable[dict[str, Any]]:
    with RECORDS_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="查询本地数学问题库。")
    parser.add_argument("--source", choices=("wikipedia", "unsolvedmath"))
    parser.add_argument("--status")
    parser.add_argument("--category", help="分类名，不区分大小写，支持子串。")
    parser.add_argument("--text", help="在标题与摘要中检索，不区分大小写。")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="输出 JSONL，而非紧凑文本。")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("limit 必须为正数。")
    return args


def matches(record: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.source and record["source"] != args.source:
        return False
    if args.status and record["status"].casefold() != args.status.casefold():
        return False
    if args.category:
        needle = args.category.casefold()
        if not any(needle in category.casefold() for category in record["categories"]):
            return False
    if args.text:
        haystack = f"{record['title']}\n{record['statement_excerpt']}".casefold()
        if args.text.casefold() not in haystack:
            return False
    return True


def main() -> int:
    args = parse_args()
    if not RECORDS_PATH.is_file():
        print("ERROR: 问题库尚未生成；先运行 scripts/fetch_problem_library.py。", file=sys.stderr)
        return 1
    emitted = 0
    for record in records():
        if not matches(record, args):
            continue
        if args.json:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
        else:
            categories = " / ".join(record["categories"])
            print(f"{record['id']}\t[{record['status']}]\t{categories}\t{record['title']}\t{record['detail_url']}")
        emitted += 1
        if emitted >= args.limit:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
