#!/usr/bin/env python3
# 校验本地问题库的覆盖率、唯一性、来源追踪、缓存哈希与索引一致性。
# 运行：python3 scripts/validate_problem_library.py
# 依赖：Python 3；不访问网络，不修改问题库。

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - 由启动环境决定
    raise SystemExit(
        "缺少 schema 校验依赖。请安装 requirements-problem-library.txt 后重试。"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "problem-library"
MANIFEST_PATH = LIBRARY / "manifest.json"
RECORDS_PATH = LIBRARY / "records" / "problems.jsonl"
CATALOG_PATH = LIBRARY / "indexes" / "catalog.json"
BY_SOURCE_PATH = LIBRARY / "indexes" / "by-source.json"
BY_CATEGORY_PATH = LIBRARY / "indexes" / "by-category.json"
SCHEMA_PATH = LIBRARY / "schema" / "problem.schema.json"

REQUIRED_FIELDS = {
    "id",
    "source",
    "source_native_id",
    "source_order",
    "source_page",
    "detail_url",
    "record_scope",
    "title",
    "statement_excerpt",
    "status",
    "difficulty",
    "categories",
    "problem_sets",
    "related_urls",
    "source_revision",
    "retrieved_at",
    "license",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with RECORDS_PATH.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"records JSONL 第 {line_number} 行无效：{exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"records JSONL 第 {line_number} 行不是对象。")
            records.append(value)
    return records


def validate() -> list[str]:
    errors: list[str] = []
    required_paths = [MANIFEST_PATH, RECORDS_PATH, CATALOG_PATH, BY_SOURCE_PATH, BY_CATEGORY_PATH, SCHEMA_PATH]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"缺少必需文件：{path.relative_to(ROOT)}")
    if errors:
        return errors
    manifest = read_json(MANIFEST_PATH)
    catalog = read_json(CATALOG_PATH)
    by_source = read_json(BY_SOURCE_PATH)
    by_category = read_json(BY_CATEGORY_PATH)
    records = load_records()
    schema = read_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    schema_validator = Draft202012Validator(schema)
    if manifest.get("records_sha256") != sha256_file(RECORDS_PATH):
        errors.append("records_sha256 与当前 problems.jsonl 不一致。")
    if manifest.get("record_count") != len(records):
        errors.append(f"manifest record_count={manifest.get('record_count')}，实际={len(records)}。")
    ids: set[str] = set()
    native_id_counts: Counter[str] = Counter()
    calculated_by_source: dict[str, list[str]] = defaultdict(list)
    calculated_by_category: dict[str, list[str]] = defaultdict(list)
    for number, record in enumerate(records, 1):
        schema_errors = sorted(schema_validator.iter_errors(record), key=lambda item: list(item.path))
        if schema_errors:
            details = "; ".join(error.message for error in schema_errors[:3])
            errors.append(f"第 {number} 条不符合 problem schema：{details}")
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            errors.append(f"第 {number} 条缺字段：{sorted(missing)}")
            continue
        record_id = record["id"]
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"第 {number} 条 id 无效。")
            continue
        if record_id in ids:
            errors.append(f"重复 id：{record_id}")
        ids.add(record_id)
        source = record["source"]
        if source not in {"wikipedia", "unsolvedmath"}:
            errors.append(f"未知来源：{source}")
        native_id = record["source_native_id"]
        if source == "unsolvedmath" and native_id:
            native_id_counts[native_id] += 1
        if not record["title"] or not record["statement_excerpt"]:
            errors.append(f"空标题或摘要：{record_id}")
        if not isinstance(record["categories"], list) or not record["categories"]:
            errors.append(f"分类缺失：{record_id}")
        license_info = record["license"]
        if not isinstance(license_info, dict) or not license_info.get("name") or not license_info.get("attribution"):
            errors.append(f"许可/归属缺失：{record_id}")
        calculated_by_source[source].append(record_id)
        for category in record["categories"]:
            calculated_by_category[category].append(record_id)
    source_counts = dict(sorted(Counter(record["source"] for record in records).items()))
    status_counts = dict(sorted(Counter(record["status"] for record in records).items()))
    category_counts = dict(
        sorted(Counter(category for record in records for category in record["categories"]).items())
    )
    if catalog.get("record_count") != len(records):
        errors.append("catalog record_count 不一致。")
    if catalog.get("source_counts") != source_counts:
        errors.append("catalog source_counts 不一致。")
    if catalog.get("status_counts") != status_counts:
        errors.append("catalog status_counts 不一致。")
    if catalog.get("category_counts") != category_counts:
        errors.append("catalog category_counts 不一致。")
    if by_source.get("items") != dict(sorted(calculated_by_source.items())):
        errors.append("by-source 索引与 records 不一致。")
    if by_category.get("items") != dict(sorted(calculated_by_category.items())):
        errors.append("by-category 索引与 records 不一致。")
    sources = manifest.get("sources", {})
    unsolved = sources.get("unsolvedmath", {})
    wikipedia = sources.get("wikipedia", {})
    if unsolved.get("record_count") != unsolved.get("expected_record_count"):
        errors.append("UnsolvedMath 实际条目数未达到目录声明总数。")
    if unsolved.get("record_count") != source_counts.get("unsolvedmath"):
        errors.append("UnsolvedMath manifest 条目数与 records 不一致。")
    anomalies = unsolved.get("identity_anomalies", {})
    calculated_conflicts = {native_id for native_id, count in native_id_counts.items() if count > 1}
    reported_conflicts = set(anomalies.get("conflicts", {}))
    if anomalies.get("distinct_native_id_count") != len(native_id_counts):
        errors.append("UnsolvedMath distinct_native_id_count 与 records 不一致。")
    if anomalies.get("conflicting_native_id_count") != len(calculated_conflicts):
        errors.append("UnsolvedMath conflicting_native_id_count 与 records 不一致。")
    if anomalies.get("excess_rows_over_distinct_native_ids") != sum(native_id_counts.values()) - len(native_id_counts):
        errors.append("UnsolvedMath excess_rows_over_distinct_native_ids 与 records 不一致。")
    if reported_conflicts != calculated_conflicts:
        errors.append("UnsolvedMath manifest 冲突 ID 集合与 records 不一致。")
    pages = unsolved.get("pages", [])
    if len(pages) != unsolved.get("page_count"):
        errors.append("UnsolvedMath 原始分页数与 page_count 不一致。")
    if [page.get("page") for page in pages] != list(range(1, len(pages) + 1)):
        errors.append("UnsolvedMath 原始分页序号不连续。")
    if sum(page.get("record_count", 0) for page in pages) != unsolved.get("record_count"):
        errors.append("UnsolvedMath 分页行数之和与 record_count 不一致。")
    for page in pages:
        raw_path = ROOT / page.get("raw_file", "")
        if not raw_path.is_file():
            errors.append(f"缺少 UnsolvedMath 原始页：{page.get('raw_file')}")
        elif sha256_file(raw_path) != page.get("raw_sha256"):
            errors.append(f"UnsolvedMath 原始页哈希漂移：{page.get('raw_file')}")
    wiki_raw = ROOT / wikipedia.get("raw_file", "")
    if not wiki_raw.is_file():
        errors.append(f"缺少 Wikipedia 原始快照：{wikipedia.get('raw_file')}")
    elif sha256_file(wiki_raw) != wikipedia.get("raw_sha256"):
        errors.append("Wikipedia 原始快照哈希漂移。")
    if wikipedia.get("record_count") != source_counts.get("wikipedia"):
        errors.append("Wikipedia manifest 条目数与 records 不一致。")
    if wikipedia.get("license", {}).get("url") != "https://creativecommons.org/licenses/by-sa/4.0/deed.en":
        errors.append("Wikipedia 许可不是抓取时 API 返回的 CC BY-SA 4.0。")
    discovery_path = ROOT / unsolved.get("discovery_file", "")
    if not discovery_path.is_file():
        errors.append(f"缺少 UnsolvedMath 来源发现证据：{unsolved.get('discovery_file')}")
    elif sha256_file(discovery_path) != unsolved.get("discovery_sha256"):
        errors.append("UnsolvedMath 来源发现证据哈希漂移。")
    discovery = unsolved.get("discovery", {})
    for name in ("robots", "sitemap"):
        item = discovery.get(name, {})
        if item.get("status") != 404 or not item.get("body_sha256") or not item.get("observed_at"):
            errors.append(f"UnsolvedMath {name} 探测证据不完整或状态不再是 404。")
    return errors


def main() -> int:
    try:
        errors = validate()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"问题库校验失败：{len(errors)} 个问题。", file=sys.stderr)
        return 1
    manifest = read_json(MANIFEST_PATH)
    sources = manifest["sources"]
    print(
        "问题库校验通过："
        f"总计 {manifest['record_count']} 条；"
        f"Wikipedia {sources['wikipedia']['record_count']}；"
        f"UnsolvedMath {sources['unsolvedmath']['record_count']} / "
        f"{sources['unsolvedmath']['expected_record_count']}，"
        f"原始分页 {sources['unsolvedmath']['page_count']}。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
