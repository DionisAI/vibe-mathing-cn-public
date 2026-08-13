#!/usr/bin/env python3
# 做什么：校验可版本化问题记录、schema、manifest 和索引，不依赖被忽略的原始网页。
# 怎么运行：python3 scripts/validate_portable_problem_library.py
# 需要什么：Python 3、jsonschema；只读，不访问网络。

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "problem-library"
MANIFEST_PATH = LIBRARY / "manifest.json"
RECORDS_PATH = LIBRARY / "records" / "problems.jsonl"
SCHEMA_PATH = LIBRARY / "schema" / "problem.schema.json"
CATALOG_PATH = LIBRARY / "indexes" / "catalog.json"
BY_SOURCE_PATH = LIBRARY / "indexes" / "by-source.json"
BY_CATEGORY_PATH = LIBRARY / "indexes" / "by-category.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    if not SCHEMA_PATH.is_file():
        print(f"ERROR: 缺少必需文件：{SCHEMA_PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1

    dataset_paths = [MANIFEST_PATH, RECORDS_PATH, CATALOG_PATH, BY_SOURCE_PATH, BY_CATEGORY_PATH]
    existing_dataset_paths = [path for path in dataset_paths if path.is_file()]
    if not existing_dataset_paths:
        try:
            schema = load_json(SCHEMA_PATH)
            Draft202012Validator.check_schema(schema)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print("可移植问题库校验通过：未携带可重建来源数据，schema 有效。")
        return 0
    if len(existing_dataset_paths) != len(dataset_paths):
        for path in dataset_paths:
            if not path.is_file():
                print(f"ERROR: 本地问题库数据不完整，缺少：{path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    try:
        manifest = load_json(MANIFEST_PATH)
        records = load_jsonl(RECORDS_PATH)
        schema = load_json(SCHEMA_PATH)
        catalog = load_json(CATALOG_PATH)
        by_source = load_json(BY_SOURCE_PATH)
        by_category = load_json(BY_CATEGORY_PATH)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        ids: set[str] = set()
        calculated_by_source: dict[str, list[str]] = defaultdict(list)
        calculated_by_category: dict[str, list[str]] = defaultdict(list)
        for position, record in enumerate(records, 1):
            for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                errors.append(f"第 {position} 条 schema 错误：{error.message}")
            record_id = record.get("id")
            if record_id in ids:
                errors.append(f"重复 id：{record_id}")
            if isinstance(record_id, str):
                ids.add(record_id)
                source = record.get("source")
                calculated_by_source[source].append(record_id)
                for category in record.get("categories", []):
                    calculated_by_category[category].append(record_id)
        source_counts = dict(sorted(Counter(item["source"] for item in records).items()))
        status_counts = dict(sorted(Counter(item["status"] for item in records).items()))
        category_counts = dict(
            sorted(Counter(category for item in records for category in item["categories"]).items())
        )
        if manifest.get("record_count") != len(records):
            errors.append("manifest record_count 与 records 不一致")
        if manifest.get("records_sha256") != sha256_file(RECORDS_PATH):
            errors.append("manifest records_sha256 与 records 不一致")
        if catalog.get("record_count") != len(records):
            errors.append("catalog record_count 与 records 不一致")
        if catalog.get("source_counts") != source_counts:
            errors.append("catalog source_counts 与 records 不一致")
        if catalog.get("status_counts") != status_counts:
            errors.append("catalog status_counts 与 records 不一致")
        if catalog.get("category_counts") != category_counts:
            errors.append("catalog category_counts 与 records 不一致")
        if by_source.get("items") != dict(sorted(calculated_by_source.items())):
            errors.append("by-source 索引与 records 不一致")
        if by_category.get("items") != dict(sorted(calculated_by_category.items())):
            errors.append("by-category 索引与 records 不一致")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"可移植问题库校验失败：{len(errors)} 个问题。", file=sys.stderr)
        return 1
    print(f"可移植问题库校验通过：{len(records)} 条来源记录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
