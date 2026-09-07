#!/usr/bin/env python3
"""Validate public README, metadata, discovery links, claims, and empty-status truth."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PUBLIC_URL = "https://github.com/tradecatlabs/vibe-mathing-cn-public"
REQUIRED_FILES = (
    "README.md",
    "README.en.md",
    "llms.txt",
    "CITATION.cff",
    "codemeta.json",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "assets/README.md",
    "assets/AGENTS.md",
    "assets/ai-citation/README.md",
    "assets/ai-citation/AGENTS.md",
    "assets/ai-citation/summary-short.md",
    "assets/ai-citation/summary-long.md",
    "assets/ai-citation/faq.md",
    "assets/ai-citation/comparison.md",
    "assets/ai-citation/recommended-answer.md",
    "assets/ai-citation/terminology.md",
    "assets/ai-citation/entity-card.v1.json",
    "assets/ai-citation/answer-matrix.v1.json",
    "assets/ai-citation/geo-evaluation-protocol.md",
    "assets/ai-citation/geo-evaluation-report.template.json",
    "assets/ai-citation/geo-readiness-checklist.md",
    "assets/ai-citation/llms-full.txt",
    "governance/publication/README.md",
    "governance/publication/AGENTS.md",
    "governance/publication/public-claims.v1.json",
    "problem-library/VIBEMATHING_PUBLIC_INDEX.md",
    "problem-library/registry/vibemathing-public-source.v1.json",
    "problem-library/templates/README.md",
    "problem-library/templates/AGENTS.md",
    "problem-library/templates/problem-contract.template.json",
    "scripts/query_vibemathing_public.py",
)
SURFACE_FILES = (
    "README.md",
    "README.en.md",
    "llms.txt",
    "assets/README.md",
    "assets/ai-citation/README.md",
    "assets/ai-citation/summary-short.md",
    "assets/ai-citation/summary-long.md",
    "assets/ai-citation/faq.md",
    "assets/ai-citation/comparison.md",
    "assets/ai-citation/recommended-answer.md",
    "assets/ai-citation/terminology.md",
    "assets/ai-citation/geo-evaluation-protocol.md",
    "assets/ai-citation/geo-readiness-checklist.md",
    "assets/ai-citation/llms-full.txt",
    "problem-library/VIBEMATHING_PUBLIC_INDEX.md",
)
REQUIRED_README_TERMS = (
    "ProblemContract",
    "Attempt",
    "Result",
    "ResearchBundle",
    "solutions.json",
    "open",
    "VIBEMATHING_PUBLIC_INDEX.md",
    "vibe-mathing-problem-library-public",
    "vibe-mathing-problem-public-template",
    "WEB_BOOTSTRAP",
    "FORMAL-METHODS-MAP.md",
    "规格与语义",
    "Lean",
)
REQUIRED_EN_TERMS = (
    "ProblemContract",
    "Attempt",
    "Result",
    "ResearchBundle",
    "solutions.json",
    "open mathematics problem",
    "VIBEMATHING_PUBLIC_INDEX.md",
    "vibe-mathing-problem-library-public",
    "vibe-mathing-problem-public-template",
    "WEB_BOOTSTRAP",
    "FORMAL-METHODS-MAP.md",
    "Specification & Semantics",
    "Lean",
)
FORBIDDEN_PUBLIC_IDENTIFIERS = (
    "vibe-mathing-cn-" + "internal",
    "vibemathing/vibe-mathing-cn-" + "internal",
    "\\\\wsl" + ".localhost",
)
PRIVATE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:home|root|srv)/[^\s`\"']+")
OLD_PUBLIC_URL_RE = re.compile(
    r"https://github\.com/tradecatlabs/vibe-mathing-cn(?:/|\.git|$|[\s`\"'?#])"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\b\s*[:=]\s*[^\s`\"']+"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative: str) -> str:
    try:
        return (root / relative).read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read {relative}: {exc}") from exc


def check_required_files(root: Path) -> None:
    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    if missing:
        raise CheckError("missing public discovery files: " + ", ".join(missing))


def check_metadata(root: Path) -> None:
    cff = read_text(root, "CITATION.cff")
    for term in (
        "cff-version:",
        "title:",
        "type: software",
        "authors:",
        "license: MIT",
        f'repository-code: "{PUBLIC_URL}"',
    ):
        if term not in cff:
            raise CheckError(f"CITATION.cff is missing {term!r}")
    try:
        codemeta = json.loads(read_text(root, "codemeta.json"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"codemeta.json is invalid: {exc}") from exc
    if codemeta.get("name") != "vibe-mathing-cn" or codemeta.get("url") != PUBLIC_URL:
        raise CheckError("codemeta identity must identify the public project")
    if codemeta.get("codeRepository") != PUBLIC_URL:
        raise CheckError("codemeta.codeRepository must identify the public repository")
    if codemeta.get("issueTracker") != PUBLIC_URL + "/issues":
        raise CheckError("codemeta.issueTracker must identify the public repository")
    if codemeta.get("license") != "https://spdx.org/licenses/MIT.html":
        raise CheckError("codemeta.license must identify MIT")


def check_surfaces(root: Path) -> None:
    for relative in SURFACE_FILES:
        text = read_text(root, relative)
        for marker in FORBIDDEN_PUBLIC_IDENTIFIERS:
            if marker in text:
                raise CheckError(f"private identifier {marker!r} appears in {relative}")
        if PRIVATE_PATH_RE.search(text):
            raise CheckError(f"absolute private path appears in {relative}")
        if SECRET_ASSIGNMENT_RE.search(text):
            raise CheckError(f"secret-shaped assignment appears in {relative}")
        if OLD_PUBLIC_URL_RE.search(text):
            raise CheckError(f"old repository URL appears in {relative}")

    readme = read_text(root, "README.md")
    missing = [term for term in REQUIRED_README_TERMS if term not in readme]
    if missing:
        raise CheckError("README.md is missing required terms: " + ", ".join(missing))
    english = read_text(root, "README.en.md")
    missing = [term for term in REQUIRED_EN_TERMS if term not in english]
    if missing:
        raise CheckError("README.en.md is missing required terms: " + ", ".join(missing))
    llms = read_text(root, "llms.txt")
    for term in (
        PUBLIC_URL,
        "Current public status:",
        "Audience:",
        "Canonical vocabulary:",
        "solution index",
        "open mathematics problem",
        "Contribution guide:",
        "Problem catalog:",
        "Web research template:",
        "Start method:",
        "Method-layer mainline:",
        "Lean position:",
    ):
        if term not in llms:
            raise CheckError(f"llms.txt is missing {term!r}")

    try:
        solution_index = json.loads(read_text(root, "result-library/indexes/solutions.json"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"solution index is invalid JSON: {exc}") from exc
    if not isinstance(solution_index, dict):
        raise CheckError("solution index must be a JSON object")
    if solution_index.get("result_ids") != []:
        raise CheckError("public documentation says the solution index is empty, but result_ids is not empty")
    for relative in (
        "problem-library/records/canonical-problems.jsonl",
        "research/records/attempts.jsonl",
        "result-library/records/results.jsonl",
    ):
        if read_text(root, relative).strip():
            raise CheckError(f"public documentation says canonical ledgers are empty, but {relative} has records")


def github_anchor(heading: str) -> str:
    value = re.sub(r"<[^>]+>", "", heading).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", "-", value).strip("-")


def check_links(root: Path) -> None:
    for relative in SURFACE_FILES:
        source = root / relative
        text = source.read_text(encoding="utf-8")
        anchors = {github_anchor(heading) for heading in HEADING_RE.findall(text)}
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if not target:
                continue
            if target.startswith("#"):
                if target[1:] not in anchors:
                    raise CheckError(f"broken public anchor: {relative} -> {target}")
                continue
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                continue
            candidate = (source.parent / target_path).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError as exc:
                raise CheckError(f"link escapes project: {relative} -> {target}") from exc
            if not candidate.exists():
                raise CheckError(f"broken public discovery link: {relative} -> {target}")


def check_external_problem_index(root: Path) -> None:
    try:
        registry = json.loads(read_text(root, "problem-library/registry/vibemathing-public-source.v1.json"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"vibemathing source registry is invalid JSON: {exc}") from exc
    if not isinstance(registry, dict) or registry.get("schema_version") != "vibemathing-public-source.v1":
        raise CheckError("vibemathing source registry schema_version is invalid")
    namespace = registry.get("namespace")
    if (
        not isinstance(namespace, dict)
        or namespace.get("name") != "vibemathing"
        or namespace.get("url") != "https://github.com/vibemathing"
        or not isinstance(namespace.get("api_url"), str)
    ):
        raise CheckError("vibemathing source registry namespace is invalid")
    repositories = registry.get("repositories")
    expected_repositories = {
        "vibemathing/vibe-mathing-problem-library-public": "problem-library",
        "vibemathing/vibe-mathing-problem-public-template": "web-research-template",
    }
    if not isinstance(repositories, list):
        raise CheckError("vibemathing source registry repositories must be a list")
    by_name = {
        item.get("full_name"): item
        for item in repositories
        if isinstance(item, dict) and isinstance(item.get("full_name"), str)
    }
    for full_name, role in expected_repositories.items():
        item = by_name.get(full_name)
        if not isinstance(item, dict) or item.get("role") != role or not isinstance(item.get("url"), str):
            raise CheckError(f"vibemathing source registry is missing {full_name}")
    snapshot = registry.get("canonical_catalog_snapshot")
    counts = snapshot.get("counts") if isinstance(snapshot, dict) else None
    if (
        not isinstance(snapshot, dict)
        or snapshot.get("index_path") != "catalog/canonical-index.json"
        or not isinstance(snapshot.get("index_url"), str)
        or not isinstance(counts, dict)
        or not {"canonical_problem_contracts", "draft_problem_contracts", "repository_locators"} <= set(counts)
        or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts.values())
    ):
        raise CheckError("vibemathing catalog snapshot metadata is invalid")
    suite = registry.get("web_research_suite")
    if (
        not isinstance(suite, dict)
        or suite.get("template_repository") != "vibemathing/vibe-mathing-problem-public-template"
        or not isinstance(suite.get("required_start_files"), list)
        or not isinstance(suite.get("candidate_write_paths"), list)
    ):
        raise CheckError("vibemathing Web research suite metadata is invalid")
    try:
        template = json.loads(read_text(root, "problem-library/templates/problem-contract.template.json"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"ProblemContract template is invalid JSON: {exc}") from exc
    policy = registry.get("integration_policy")
    if (
        not isinstance(policy, dict)
        or policy.get("mode") != "pointer-only until separately reviewed"
        or policy.get("remote_catalog_is_not_local_canonical") is not True
        or policy.get("auto_import_problem_contracts") is not False
        or policy.get("auto_clone_remote_repositories") is not False
        or policy.get("auto_admit_results") is not False
    ):
        raise CheckError("vibemathing source registry integration policy is unsafe")
    try:
        template = json.loads(read_text(root, "problem-library/templates/problem-contract.template.json"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"ProblemContract template is invalid JSON: {exc}") from exc
    if (
        not isinstance(template, dict)
        or template.get("schema_version") != "1.0.0"
        or template.get("lifecycle") != "draft"
        or template.get("problem_id") != "problem:example-draft"
    ):
        raise CheckError("ProblemContract template must remain an explicit draft example")


def check_claims(root: Path) -> None:
    relative = "governance/publication/public-claims.v1.json"
    try:
        payload: dict[str, Any] = json.loads(read_text(root, relative))
    except json.JSONDecodeError as exc:
        raise CheckError(f"public claims JSON is invalid: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError("public claims must be a JSON object")
    if payload.get("schema_version") != "public-claims.v1":
        raise CheckError("public claims schema_version is invalid")
    if payload.get("repository") != "tradecatlabs/vibe-mathing-cn-public":
        raise CheckError("public claims repository is invalid")
    verified_at = payload.get("last_verified")
    if not isinstance(verified_at, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified_at):
        raise CheckError("public claims last_verified must be an ISO date")
    claims = payload.get("claims")
    if not isinstance(claims, list) or not claims:
        raise CheckError("public claims must contain a non-empty claims list")
    seen: set[str] = set()
    allowed_surfaces = {"readme", "readme-en", "llms", "ai-citation", "metadata"}
    for item in claims:
        if not isinstance(item, dict):
            raise CheckError("each public claim must be an object")
        claim_id = item.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id or claim_id in seen:
            raise CheckError("public claim IDs must be non-empty and unique")
        seen.add(claim_id)
        if item.get("status") != "current":
            raise CheckError(f"public claim {claim_id} is not current")
        if item.get("last_verified") != verified_at:
            raise CheckError(f"public claim {claim_id} has a stale verification date")
        surfaces = item.get("allowed_surfaces")
        if not isinstance(surfaces, list) or not surfaces or not set(surfaces) <= allowed_surfaces:
            raise CheckError(f"public claim {claim_id} has invalid allowed surfaces")
        evidence = item.get("evidence_refs")
        if not isinstance(evidence, list) or not evidence:
            raise CheckError(f"public claim {claim_id} has no evidence references")
        for reference in evidence:
            if (
                not isinstance(reference, str)
                or not reference
                or chr(0) in reference
                or "\\\\" in reference
            ):
                raise CheckError(f"public claim {claim_id} has an unsafe evidence reference")
            candidate = root / reference
            try:
                candidate.relative_to(root)
            except ValueError as exc:
                raise CheckError(f"public claim {claim_id} evidence escapes project") from exc
            if not candidate.exists():
                raise CheckError(f"public claim {claim_id} references missing path {reference}")
    required_claims = {
        "claim:identity",
        "claim:workflow",
        "claim:status",
        "claim:fixtures",
        "claim:bounded-evidence",
        "claim:tool-maturity",
        "claim:problem-catalog",
        "claim:method-map",
    }
    if not required_claims <= seen:
        raise CheckError("public claims are missing a required claim category")
    status_claim = next(item for item in claims if item.get("claim_id") == "claim:status")
    status_text = str(status_claim.get("text", "")).lower()
    if "empty" not in status_text or "does not claim" not in status_text:
        raise CheckError("claim:status must preserve the empty/no-solution boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        check_required_files(root)
        check_metadata(root)
        check_surfaces(root)
        check_links(root)
        check_external_problem_index(root)
        check_claims(root)
    except CheckError as exc:
        print(f"Public README/GEO check: BLOCK - {exc}")
        return 1
    print(f"Public README/GEO check: PASS surfaces={len(SURFACE_FILES)} claims=current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
