#!/usr/bin/env python3
# 抓取 Wikipedia 与 UnsolvedMath 的公开问题目录，并生成可追溯的本地问题库。
# 运行：python3 scripts/fetch_problem_library.py [--refresh] [--delay 0.25]
# 依赖：Python 3、beautifulsoup4、lxml 与可访问两个来源站点的网络。

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from bs4 import BeautifulSoup, Tag
except ImportError as exc:  # pragma: no cover - 由启动环境决定
    raise SystemExit(
        "缺少解析依赖。请安装 requirements-problem-library.txt 后重试。"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "problem-library"
RAW_WIKIPEDIA = LIBRARY / "raw" / "wikipedia"
RAW_UNSOLVEDMATH = LIBRARY / "raw" / "unsolvedmath"
RECORDS_PATH = LIBRARY / "records" / "problems.jsonl"
MANIFEST_PATH = LIBRARY / "manifest.json"
CATALOG_PATH = LIBRARY / "indexes" / "catalog.json"
BY_SOURCE_PATH = LIBRARY / "indexes" / "by-source.json"
BY_CATEGORY_PATH = LIBRARY / "indexes" / "by-category.json"

USER_AGENT = "vibe-mathing-problem-library/0.1 (local research archive)"
WIKIPEDIA_PAGE = "List of unsolved problems in mathematics"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics"
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
UNSOLVEDMATH_URL = "https://www.unsolvedmath.com/problems"
SCHEMA_VERSION = "1.0.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_timestamp(path: Path) -> str:
    return (
        datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write_atomic(path, payload.encode("utf-8"))


class Fetcher:
    def __init__(self, *, timeout: float, delay: float, retries: int) -> None:
        self.timeout = timeout
        self.delay = delay
        self.retries = retries
        self._last_request_at = 0.0

    def fetch(self, url: str) -> tuple[bytes, dict[str, str]]:
        error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            elapsed = time.monotonic() - self._last_request_at
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
            request = urllib.request.Request(
                url,
                headers={
                    "Accept": "text/html,application/json;q=0.9,*/*;q=0.1",
                    "Accept-Encoding": "identity",
                    "User-Agent": USER_AGENT,
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                    headers = {key.lower(): value for key, value in response.headers.items()}
                    self._last_request_at = time.monotonic()
                    return body, headers
            except (urllib.error.URLError, TimeoutError) as exc:
                self._last_request_at = time.monotonic()
                error = exc
                if attempt < self.retries:
                    time.sleep(min(2 ** (attempt - 1), 8))
        raise RuntimeError(f"抓取失败（重试 {self.retries} 次）：{url}: {error}") from error

    def probe(self, url: str) -> dict[str, Any]:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        request = urllib.request.Request(
            url,
            headers={"Accept-Encoding": "identity", "User-Agent": USER_AGENT},
        )
        observed_at = utc_now()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                status = response.status
                headers = response.headers
        except urllib.error.HTTPError as exc:
            body = exc.read()
            status = exc.code
            headers = exc.headers
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"来源发现探测失败：{url}: {exc}") from exc
        finally:
            self._last_request_at = time.monotonic()
        return {
            "url": url,
            "status": status,
            "observed_at": observed_at,
            "body_sha256": sha256_bytes(body),
            "content_type": headers.get("Content-Type"),
            "etag": headers.get("ETag"),
            "last_modified": headers.get("Last-Modified"),
        }


def cached_fetch(
    fetcher: Fetcher,
    url: str,
    path: Path,
    *,
    refresh: bool,
) -> tuple[bytes, dict[str, str], bool]:
    if path.is_file() and not refresh:
        return path.read_bytes(), {}, True
    body, headers = fetcher.fetch(url)
    if not body:
        raise RuntimeError(f"来源返回空响应：{url}")
    write_atomic(path, body)
    return body, headers, False


def wikipedia_api_url(parameters: dict[str, str]) -> str:
    return f"{WIKIPEDIA_API}?{urllib.parse.urlencode(parameters)}"


def replace_math_and_remove_noise(node: Tag) -> None:
    for math_node in node.select(".mwe-math-element"):
        annotation = math_node.select_one('annotation[encoding="application/x-tex"]')
        replacement = normalize_space(annotation.get_text(" ", strip=True)) if annotation else ""
        replacement = re.sub(r"^\{\\displaystyle\s*", "", replacement)
        replacement = re.sub(r"\}\s*$", "", replacement)
        math_node.replace_with(f" ${replacement}$ " if replacement else " ")
    for selector in ("sup.reference", ".mw-editsection", "style", "script"):
        for noisy_node in node.select(selector):
            noisy_node.decompose()


def wikipedia_item_text(item: Tag) -> str:
    clone = BeautifulSoup(str(item), "lxml").find("li")
    if clone is None:
        return ""
    for nested in clone.find_all(["ul", "ol"], recursive=False):
        nested.decompose()
    replace_math_and_remove_noise(clone)
    return normalize_space(clone.get_text(" ", strip=True))


def wikipedia_item_title(item: Tag, statement: str) -> str:
    links = [
        normalize_space(link.get_text(" ", strip=True))
        for link in item.select('a[href^="./"], a[href^="/wiki/"]')
        if normalize_space(link.get_text(" ", strip=True))
    ]
    if links:
        candidate = links[0]
        prefix = statement[: max(len(candidate) + 8, 40)].casefold()
        if candidate.casefold() in prefix or re.search(
            r"(conjecture|problem|hypothesis|question|theorem|equation|constant)",
            candidate,
            flags=re.IGNORECASE,
        ):
            return candidate[:240]
    for separator in (":", " – ", " — "):
        head, found, _ = statement.partition(separator)
        if found and 3 <= len(head) <= 240:
            return head.strip()
    sentence = re.split(r"(?<=[?.!])\s+", statement, maxsplit=1)[0]
    return sentence[:240].rstrip()


def iter_section_list_items(soup: BeautifulSoup) -> Iterable[tuple[str, list[str], Tag]]:
    active = False
    status = ""
    category_path: list[str] = []
    for node in soup.find_all(recursive=False):
        heading = node if node.name in {"h2", "h3", "h4"} else node.find(
            ["h2", "h3", "h4"], recursive=False
        ) if isinstance(node, Tag) else None
        if heading is not None:
            level = int(heading.name[1])
            title = normalize_space(heading.get_text(" ", strip=True))
            anchor_node = heading.find(id=True)
            anchor = anchor_node.get("id", "") if anchor_node else heading.get("id", "")
            if level == 2:
                if anchor == "Unsolved_problems":
                    active = True
                    status = "open"
                    category_path = []
                elif anchor == "Problems_solved_since_1995":
                    active = True
                    status = "solved_since_1995"
                    category_path = []
                elif active:
                    active = False
                continue
            if active and level == 3:
                category_path = [title]
            elif active and level == 4:
                category_path = category_path[:1] + [title]
            continue
        if not active or not isinstance(node, Tag) or node.name not in {"ul", "ol"}:
            continue
        for item in node.find_all("li", recursive=False):
            yield status, category_path.copy(), item


def parse_wikipedia(
    raw: dict[str, Any],
    *,
    retrieved_at: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    parsed = raw["parse"]
    page = raw["page"]
    rights = raw["rights"]
    soup = BeautifulSoup(parsed["text"], "lxml")
    root = soup.select_one(".mw-parser-output") or soup.body or soup
    records: list[dict[str, Any]] = []
    order = 0
    for status, category_path, item in iter_section_list_items(root):
        statement = wikipedia_item_text(item)
        if not statement:
            continue
        order += 1
        title = wikipedia_item_title(item, statement)
        identity = f"{status}\x1f{'/'.join(category_path)}\x1f{statement}".encode("utf-8")
        record_id = f"wikipedia-{hashlib.sha1(identity).hexdigest()[:16]}"
        links: list[str] = []
        for link in item.select("a[href]"):
            href = link.get("href", "")
            if href.startswith("./"):
                links.append(urllib.parse.urljoin(WIKIPEDIA_URL, href[2:]))
            elif href.startswith("/wiki/"):
                links.append(urllib.parse.urljoin("https://en.wikipedia.org", href))
        records.append(
            {
                "id": record_id,
                "source": "wikipedia",
                "source_native_id": None,
                "source_order": order,
                "source_page": WIKIPEDIA_URL,
                "detail_url": links[0] if links else WIKIPEDIA_URL,
                "record_scope": "list_item",
                "title": title,
                "statement_excerpt": statement,
                "status": status,
                "difficulty": None,
                "categories": category_path,
                "problem_sets": [],
                "related_urls": list(dict.fromkeys(links)),
                "source_revision": {
                    "page_id": page["pageid"],
                    "revision_id": page["revisions"][0]["revid"],
                    "timestamp": page["revisions"][0]["timestamp"],
                    "sha1": page["revisions"][0]["sha1"],
                },
                "retrieved_at": retrieved_at,
                "license": {
                    "name": rights["text"],
                    "url": rights["url"],
                    "attribution": f'Wikipedia contributors, "{WIKIPEDIA_PAGE}"',
                },
            }
        )
    if not records:
        raise RuntimeError("Wikipedia 解析结果为空；页面结构可能已变化。")
    metadata = {
        "page_id": page["pageid"],
        "revision_id": page["revisions"][0]["revid"],
        "revision_timestamp": page["revisions"][0]["timestamp"],
        "revision_sha1": page["revisions"][0]["sha1"],
        "license": rights,
        "record_count": len(records),
        "status_counts": dict(sorted(Counter(item["status"] for item in records).items())),
    }
    return records, metadata


def fetch_wikipedia(
    fetcher: Fetcher,
    *,
    refresh: bool,
    retrieved_at: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_path = RAW_WIKIPEDIA / "list-of-unsolved-problems.json"
    if raw_path.is_file() and not refresh:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        from_cache = True
    else:
        parse_url = wikipedia_api_url(
            {
                "action": "parse",
                "page": WIKIPEDIA_PAGE,
                "prop": "text|sections",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
        )
        page_url = wikipedia_api_url(
            {
                "action": "query",
                "titles": WIKIPEDIA_PAGE,
                "prop": "revisions",
                "rvprop": "ids|timestamp|sha1",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
        )
        rights_url = wikipedia_api_url(
            {
                "action": "query",
                "meta": "siteinfo",
                "siprop": "rightsinfo",
                "format": "json",
                "formatversion": "2",
            }
        )
        parse_body, _ = fetcher.fetch(parse_url)
        page_body, _ = fetcher.fetch(page_url)
        rights_body, _ = fetcher.fetch(rights_url)
        parse_data = json.loads(parse_body)
        page_data = json.loads(page_body)
        rights_data = json.loads(rights_body)
        if "error" in parse_data or "error" in page_data or "error" in rights_data:
            raise RuntimeError("Wikipedia API 返回错误，拒绝生成不完整快照。")
        raw = {
            "retrieved_at": retrieved_at,
            "request_urls": [parse_url, page_url, rights_url],
            "parse": parse_data["parse"],
            "page": page_data["query"]["pages"][0],
            "rights": rights_data["query"]["rightsinfo"],
        }
        write_json(raw_path, raw)
        from_cache = False
    records, metadata = parse_wikipedia(raw, retrieved_at=raw.get("retrieved_at", retrieved_at))
    metadata.update(
        {
            "source_url": WIKIPEDIA_URL,
            "raw_file": str(raw_path.relative_to(ROOT)),
            "raw_sha256": sha256_bytes(raw_path.read_bytes()),
            "from_cache": from_cache,
            "record_scope": "all direct list items in the open and solved-since-1995 sections",
        }
    )
    return records, metadata


def listing_summary(soup: BeautifulSoup) -> tuple[int, int]:
    pattern = re.compile(r"Showing\s+\d+\s*-\s*\d+\s+of\s+([\d,]+)\s+problems\s*\(Page\s+\d+\s+of\s+([\d,]+)\)")
    match = pattern.search(normalize_space(soup.get_text(" ", strip=True)))
    if not match:
        raise RuntimeError("无法从 UnsolvedMath 目录页识别总条目数和页数。")
    return int(match.group(1).replace(",", "")), int(match.group(2).replace(",", ""))


def parse_unsolvedmath_card(card: Tag, *, page_number: int, order: int, retrieved_at: str) -> dict[str, Any]:
    href = card.get("href", "")
    detail_url = urllib.parse.urljoin(UNSOLVEDMATH_URL, href)
    native_id_node = card.select_one("span.font-mono")
    title_node = card.select_one("h3")
    excerpt_node = card.select_one("p")
    badges = card.select("div.inline-flex.items-center.rounded-md.border")
    if native_id_node is None or title_node is None or excerpt_node is None or len(badges) < 2:
        raise RuntimeError(f"UnsolvedMath 第 {page_number} 页卡片结构不完整：{detail_url}")
    native_id = normalize_space(native_id_node.get_text(" ", strip=True))
    title = normalize_space(title_node.get_text(" ", strip=True))
    excerpt = normalize_space(excerpt_node.get_text(" ", strip=True))
    excerpt = re.sub(r"\s*\.\.\.\s*$", "", excerpt).rstrip()
    status_label = normalize_space(badges[0].get_text(" ", strip=True))
    difficulty_label = normalize_space(badges[1].get_text(" ", strip=True))
    difficulty_match = re.search(r"(\d+)", difficulty_label)
    category_nodes = [
        node
        for node in card.select("span.text-xs.text-gray-500")
        if "font-mono" not in (node.get("class") or [])
    ]
    if not native_id or not title or difficulty_match is None or not category_nodes:
        raise RuntimeError(f"UnsolvedMath 第 {page_number} 页卡片字段缺失：{detail_url}")
    status_map = {
        "open": "open",
        "partially solved": "partially_solved",
        "solved": "solved",
    }
    status = status_map.get(status_label.casefold())
    if status is None:
        raise RuntimeError(f"未知 UnsolvedMath 状态 {status_label!r}：{detail_url}")
    category = normalize_space(category_nodes[-1].get_text(" ", strip=True))
    identity = json.dumps(
        [native_id, title, excerpt, status, int(difficulty_match.group(1)), category],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    identity_digest = hashlib.sha1(identity).hexdigest()[:12]
    return {
        "id": f"unsolvedmath-{native_id.casefold()}-{identity_digest}",
        "source": "unsolvedmath",
        "source_native_id": native_id,
        "source_order": order,
        "source_page": f"{UNSOLVEDMATH_URL}?page={page_number}",
        "detail_url": detail_url,
        "record_scope": "listing_card",
        "title": title,
        "statement_excerpt": excerpt,
        "status": status,
        "difficulty": int(difficulty_match.group(1)),
        "categories": [category],
        "problem_sets": [],
        "related_urls": [],
        "source_revision": None,
        "retrieved_at": retrieved_at,
        "license": {
            "name": "unknown",
            "url": None,
            "attribution": "UnsolvedMath",
        },
    }


def fetch_unsolvedmath(
    fetcher: Fetcher,
    *,
    refresh: bool,
    retrieved_at: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    discovery_path = RAW_UNSOLVEDMATH / "discovery.json"
    if refresh or not discovery_path.is_file():
        discovery = {
            "robots": fetcher.probe("https://www.unsolvedmath.com/robots.txt"),
            "sitemap": fetcher.probe("https://www.unsolvedmath.com/sitemap.xml"),
        }
        write_json(discovery_path, discovery)
    else:
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    first_path = RAW_UNSOLVEDMATH / "page-001.html"
    first_body, _, first_from_cache = cached_fetch(
        fetcher,
        f"{UNSOLVEDMATH_URL}?page=1",
        first_path,
        refresh=refresh,
    )
    first_soup = BeautifulSoup(first_body, "lxml")
    expected_total, page_count = listing_summary(first_soup)
    records: list[dict[str, Any]] = []
    page_entries: list[dict[str, Any]] = []
    local_id_occurrences: Counter[str] = Counter()
    order = 0
    cache_hits = int(first_from_cache)
    for page_number in range(1, page_count + 1):
        raw_path = RAW_UNSOLVEDMATH / f"page-{page_number:03d}.html"
        if page_number == 1:
            body = first_body
            from_cache = first_from_cache
        else:
            body, _, from_cache = cached_fetch(
                fetcher,
                f"{UNSOLVEDMATH_URL}?page={page_number}",
                raw_path,
                refresh=refresh,
            )
            cache_hits += int(from_cache)
        page_retrieved_at = file_timestamp(raw_path)
        soup = BeautifulSoup(body, "lxml")
        cards_by_url: dict[str, Tag] = {}
        for card in soup.select('a[href^="/problems/"]'):
            cards_by_url.setdefault(urllib.parse.urljoin(UNSOLVEDMATH_URL, card.get("href", "")), card)
        if not cards_by_url:
            raise RuntimeError(f"UnsolvedMath 第 {page_number}/{page_count} 页没有问题卡片。")
        page_record_ids: list[str] = []
        for card in cards_by_url.values():
            order += 1
            record = parse_unsolvedmath_card(
                card,
                page_number=page_number,
                order=order,
                retrieved_at=page_retrieved_at,
            )
            local_id_occurrences[record["id"]] += 1
            if local_id_occurrences[record["id"]] > 1:
                record["id"] = f"{record['id']}-{local_id_occurrences[record['id']]}"
            records.append(record)
            page_record_ids.append(record["id"])
        page_entries.append(
            {
                "page": page_number,
                "raw_file": str(raw_path.relative_to(ROOT)),
                "raw_sha256": sha256_bytes(body),
                "retrieved_at": page_retrieved_at,
                "record_count": len(page_record_ids),
                "first_record_id": page_record_ids[0],
                "last_record_id": page_record_ids[-1],
            }
        )
        if page_number == 1 or page_number == page_count or page_number % 10 == 0:
            print(f"UnsolvedMath：已解析 {page_number}/{page_count} 页，累计 {len(records)} 条", flush=True)
    unique_ids = {record["id"] for record in records}
    if len(records) != expected_total:
        raise RuntimeError(
            f"UnsolvedMath 覆盖率失败：目录声明 {expected_total} 条，实际解析 {len(records)} 条。"
        )
    if len(unique_ids) != len(records):
        raise RuntimeError("本地内容指纹 ID 仍然重复，拒绝生成不确定快照。")
    native_id_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        native_id_groups[record["source_native_id"]].append(
            {
                "record_id": record["id"],
                "page": int(urllib.parse.parse_qs(urllib.parse.urlparse(record["source_page"]).query)["page"][0]),
                "title": record["title"],
                "detail_url": record["detail_url"],
            }
        )
    identity_conflicts = {
        native_id: occurrences
        for native_id, occurrences in sorted(native_id_groups.items())
        if len(occurrences) > 1
    }
    metadata = {
        "source_url": UNSOLVEDMATH_URL,
        "record_scope": "all server-rendered listing cards; detail bodies are not mirrored",
        "license": {
            "name": "unknown",
            "url": None,
            "policy": "保留来源链接与简短目录摘要；未经许可不复制详情全文。",
        },
        "discovery": discovery,
        "discovery_file": str(discovery_path.relative_to(ROOT)),
        "discovery_sha256": sha256_bytes(discovery_path.read_bytes()),
        "expected_record_count": expected_total,
        "record_count": len(records),
        "page_count": page_count,
        "cache_hits": cache_hits,
        "identity_anomalies": {
            "policy": "保留每个目录行；本地主键使用内容指纹，不把重复的源 ID/URL 当作唯一键。",
            "distinct_native_id_count": len(native_id_groups),
            "conflicting_native_id_count": len(identity_conflicts),
            "excess_rows_over_distinct_native_ids": len(records) - len(native_id_groups),
            "conflicts": identity_conflicts,
        },
        "pages": page_entries,
        "status_counts": dict(sorted(Counter(item["status"] for item in records).items())),
    }
    return records, metadata


def build_indexes(records: list[dict[str, Any]], *, generated_at: str) -> dict[str, Any]:
    by_source: dict[str, list[str]] = defaultdict(list)
    by_category: dict[str, list[str]] = defaultdict(list)
    for record in records:
        by_source[record["source"]].append(record["id"])
        for category in record["categories"]:
            by_category[category].append(record["id"])
    write_json(
        BY_SOURCE_PATH,
        {"schema_version": SCHEMA_VERSION, "generated_at": generated_at, "items": dict(sorted(by_source.items()))},
    )
    write_json(
        BY_CATEGORY_PATH,
        {"schema_version": SCHEMA_VERSION, "generated_at": generated_at, "items": dict(sorted(by_category.items()))},
    )
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "record_count": len(records),
        "source_counts": dict(sorted(Counter(record["source"] for record in records).items())),
        "status_counts": dict(sorted(Counter(record["status"] for record in records).items())),
        "category_counts": dict(
            sorted(Counter(category for record in records for category in record["categories"]).items())
        ),
    }
    write_json(CATALOG_PATH, catalog)
    return catalog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取并重建本地数学问题库。")
    parser.add_argument("--refresh", action="store_true", help="忽略现有原始缓存并重新访问来源。")
    parser.add_argument("--delay", type=float, default=0.25, help="同一进程两次 HTTP 请求的最小间隔秒数。")
    parser.add_argument("--timeout", type=float, default=30.0, help="单次 HTTP 请求超时秒数。")
    parser.add_argument("--retries", type=int, default=3, help="瞬时网络失败的最大尝试次数。")
    args = parser.parse_args()
    if args.delay < 0 or args.timeout <= 0 or args.retries < 1:
        parser.error("delay 必须非负，timeout/retries 必须为正数。")
    return args


def main() -> int:
    args = parse_args()
    generated_at = utc_now()
    fetcher = Fetcher(timeout=args.timeout, delay=args.delay, retries=args.retries)
    wikipedia_records, wikipedia_metadata = fetch_wikipedia(
        fetcher,
        refresh=args.refresh,
        retrieved_at=generated_at,
    )
    print(f"Wikipedia：已解析 {len(wikipedia_records)} 条", flush=True)
    unsolvedmath_records, unsolvedmath_metadata = fetch_unsolvedmath(
        fetcher,
        refresh=args.refresh,
        retrieved_at=generated_at,
    )
    records = wikipedia_records + unsolvedmath_records
    payload = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    write_atomic(RECORDS_PATH, payload.encode("utf-8"))
    catalog = build_indexes(records, generated_at=generated_at)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "generator": "scripts/fetch_problem_library.py",
        "records_file": str(RECORDS_PATH.relative_to(ROOT)),
        "records_sha256": sha256_bytes(RECORDS_PATH.read_bytes()),
        "record_count": len(records),
        "catalog": catalog,
        "sources": {
            "wikipedia": wikipedia_metadata,
            "unsolvedmath": unsolvedmath_metadata,
        },
    }
    write_json(MANIFEST_PATH, manifest)
    print(
        f"完成：{len(records)} 条（Wikipedia {len(wikipedia_records)}；"
        f"UnsolvedMath {len(unsolvedmath_records)}），清单写入 {MANIFEST_PATH.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
