#!/usr/bin/env python3
# 校验电子书 Work/Edition/File/Relation 目录、引用完整性和本地文件摘要。
# 运行：python3 scripts/validate_literature.py
# 依赖：Python 3、jsonschema；只读访问 literature/，不修改电子书。

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
LITERATURE = ROOT / "literature"
CATALOG = LITERATURE / "catalog"
SCHEMA_PATH = LITERATURE / "schema" / "literature-records.schema.json"
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
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.relative_to(ROOT)}:{line_number}: JSON 无效：{exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path.relative_to(ROOT)}:{line_number}: 记录不是对象。")
            records.append(value)
    return records


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    records = {kind: load_jsonl(path) for kind, path in FILES.items()}
    all_ids: dict[str, str] = {}
    id_fields = {"work": "work_id", "edition": "edition_id", "file": "file_id", "relation": "relation_id"}
    for kind, items in records.items():
        validator = Draft202012Validator({"$ref": f"#/$defs/{kind}", "$defs": schema["$defs"]})
        for position, record in enumerate(items, 1):
            for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                errors.append(f"{kind} 第 {position} 条 schema 错误：{error.message}")
            record_id = record.get(id_fields[kind])
            if record_id in all_ids:
                errors.append(f"重复 ID：{record_id}")
            elif isinstance(record_id, str):
                all_ids[record_id] = kind

    work_ids = {record["work_id"] for record in records["work"]}
    edition_ids = {record["edition_id"] for record in records["edition"]}
    file_ids = {record["file_id"] for record in records["file"]}
    for edition in records["edition"]:
        if edition["work_id"] not in work_ids:
            errors.append(f"Edition 引用不存在的 Work：{edition['work_id']}")
        if not isbn13_valid(edition["isbn13"]):
            errors.append(f"ISBN-13 校验位错误：{edition['isbn13']}")
    for file_record in records["file"]:
        if file_record["edition_id"] not in edition_ids:
            errors.append(f"File 引用不存在的 Edition：{file_record['edition_id']}")
        path = (ROOT / file_record["path"]).resolve()
        try:
            path.relative_to((LITERATURE / "files").resolve())
        except ValueError:
            errors.append(f"电子书路径越出 literature/files：{file_record['path']}")
            continue
        if not path.is_file():
            errors.append(f"电子书文件不存在：{file_record['path']}")
            continue
        if path.stat().st_size != file_record["size_bytes"]:
            errors.append(f"电子书大小漂移：{file_record['path']}")
        if sha256_file(path) != file_record["sha256"]:
            errors.append(f"电子书 SHA-256 漂移：{file_record['path']}")
    entity_ids = work_ids | edition_ids | file_ids
    expected_relations = {
        (edition["work_id"], "has_edition", edition["edition_id"])
        for edition in records["edition"]
    } | {
        (file_record["edition_id"], "has_file", file_record["file_id"])
        for file_record in records["file"]
    }
    actual_relations = {
        (relation["subject_id"], relation["predicate"], relation["object_id"])
        for relation in records["relation"]
    }
    for relation in records["relation"]:
        if relation["subject_id"] not in entity_ids:
            errors.append(f"Relation subject 不存在：{relation['subject_id']}")
        if relation["object_id"] not in entity_ids and relation["predicate"] in {"has_edition", "has_file"}:
            errors.append(f"Relation object 不存在：{relation['object_id']}")
    for relation in sorted(expected_relations - actual_relations):
        errors.append(f"缺少结构关系：{relation}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"文献库校验失败：{len(errors)} 个问题。", file=sys.stderr)
        return 1
    print(
        "文献库校验通过："
        f"Work {len(records['work'])}；Edition {len(records['edition'])}；"
        f"File {len(records['file'])}；Relation {len(records['relation'])}。"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
