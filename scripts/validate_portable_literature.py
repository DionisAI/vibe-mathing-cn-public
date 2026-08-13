#!/usr/bin/env python3
# 做什么：校验可版本化的文献目录、schema 和引用，不依赖本地电子书二进制。
# 怎么运行：python3 scripts/validate_portable_literature.py
# 需要什么：Python 3、jsonschema；只读，不访问电子书文件。

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "literature" / "catalog"
SCHEMA_PATH = ROOT / "literature" / "schema" / "literature-records.schema.json"
FILES = {
    "work": CATALOG / "works.jsonl",
    "edition": CATALOG / "editions.jsonl",
    "file": CATALOG / "files.jsonl",
    "relation": CATALOG / "relations.jsonl",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path.relative_to(ROOT)}:{line_number}: 记录不是对象")
            records.append(value)
    return records


def isbn13_valid(value: str) -> bool:
    if len(value) != 13 or not value.isdigit():
        return False
    total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(value[:12]))
    return (10 - total % 10) % 10 == int(value[-1])


def main() -> int:
    errors: list[str] = []
    required = [SCHEMA_PATH, *FILES.values()]
    for path in required:
        if not path.is_file():
            errors.append(f"缺少必需文件：{path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        records = {kind: load_jsonl(path) for kind, path in FILES.items()}
        all_ids: set[str] = set()
        id_fields = {"work": "work_id", "edition": "edition_id", "file": "file_id", "relation": "relation_id"}
        for kind, items in records.items():
            validator = Draft202012Validator({"$ref": f"#/$defs/{kind}", "$defs": schema["$defs"]})
            for position, record in enumerate(items, 1):
                for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                    errors.append(f"{kind} 第 {position} 条 schema 错误：{error.message}")
                record_id = record.get(id_fields[kind])
                if record_id in all_ids:
                    errors.append(f"重复 ID：{record_id}")
                if isinstance(record_id, str):
                    all_ids.add(record_id)
        work_ids = {item["work_id"] for item in records["work"]}
        edition_ids = {item["edition_id"] for item in records["edition"]}
        file_ids = {item["file_id"] for item in records["file"]}
        for edition in records["edition"]:
            if edition["work_id"] not in work_ids:
                errors.append(f"Edition 引用不存在的 Work：{edition['work_id']}")
            if not isbn13_valid(edition["isbn13"]):
                errors.append(f"ISBN-13 校验位错误：{edition['isbn13']}")
        for item in records["file"]:
            if item["edition_id"] not in edition_ids:
                errors.append(f"File 引用不存在的 Edition：{item['edition_id']}")
            if not item["path"].startswith("literature/files/"):
                errors.append(f"File 路径越出 literature/files：{item['path']}")
        entity_ids = work_ids | edition_ids | file_ids
        for relation in records["relation"]:
            if relation["subject_id"] not in entity_ids:
                errors.append(f"Relation subject 不存在：{relation['subject_id']}")
            if relation["predicate"] in {"has_edition", "has_file"} and relation["object_id"] not in entity_ids:
                errors.append(f"Relation object 不存在：{relation['object_id']}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"可移植文献库校验失败：{len(errors)} 个问题。", file=sys.stderr)
        return 1
    print(
        "可移植文献库校验通过："
        f"Work {len(records['work'])}；Edition {len(records['edition'])}；"
        f"File {len(records['file'])}；Relation {len(records['relation'])}。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
