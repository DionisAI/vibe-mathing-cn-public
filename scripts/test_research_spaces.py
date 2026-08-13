#!/usr/bin/env python3
# 做什么：用正反例验证二维状态和完整解派生规则。
# 怎么运行：python3 scripts/test_research_spaces.py
# 需要什么：Python 3；导入项目研究空间校验器，不读写业务记录。

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_research_spaces.py"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("validate_research_spaces", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载校验器：{VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence(
    evidence_id: str,
    capability: str,
    *,
    verdict: str = "accept",
    independent: bool = True,
    invalidates: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "capability": capability,
        "verdict": verdict,
        "verifier": "independent-test-verifier",
        "independent": independent,
        "locator": "artifacts/test.txt",
        "sha256": "0" * 64,
        "checked_at": "2026-08-13T00:00:00Z",
        "invalidates": invalidates or [],
        "notes": "晋升规则回归测试",
    }


def result_record(
    *,
    result_id: str,
    kind: str,
    outcome: str,
    evidence_records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "problem_id": "problem:test",
        "attempt_id": "attempt:test",
        "kind": kind,
        "claim": "测试声明",
        "scope": "测试定义域",
        "outcome": outcome,
        "evidence": evidence_records,
        "created_at": "2026-08-13T00:00:00Z",
    }


def main() -> int:
    validator = load_validator()
    attempts_by_id = {
        "attempt:test": {
            "attempt_id": "attempt:test",
            "problem_id": "problem:test",
            "generator": "candidate-generator",
        }
    }
    valid_proof = result_record(
        result_id="result:valid-proof",
        kind="proof",
        outcome="established",
        evidence_records=[
            evidence("evidence:valid-proof-review", "human_review"),
            evidence("evidence:valid-proof-faithfulness", "statement_faithfulness"),
        ],
    )
    valid_counterexample = result_record(
        result_id="result:valid-counterexample",
        kind="counterexample",
        outcome="refuted",
        evidence_records=[
            evidence("evidence:valid-counterexample-check", "counterexample_check"),
            evidence("evidence:valid-counterexample-faithfulness", "statement_faithfulness"),
        ],
    )
    finite_evidence = result_record(
        result_id="result:finite-evidence",
        kind="numerical_evidence",
        outcome="supported",
        evidence_records=[evidence("evidence:finite-numeric", "numeric_check")],
    )
    false_numeric_solution = result_record(
        result_id="result:false-numeric-solution",
        kind="numerical_evidence",
        outcome="established",
        evidence_records=[evidence("evidence:false-numeric", "numeric_check")],
    )
    self_reviewed_proof = result_record(
        result_id="result:self-reviewed-proof",
        kind="proof",
        outcome="established",
        evidence_records=[
            evidence("evidence:self-review", "human_review", independent=False),
            evidence("evidence:self-review-faithfulness", "statement_faithfulness"),
        ],
    )
    unfaithful_formalization = result_record(
        result_id="result:unfaithful-formalization",
        kind="proof",
        outcome="established",
        evidence_records=[
            evidence("evidence:unfaithful-kernel", "kernel_check"),
            evidence(
                "evidence:unfaithful-statement",
                "statement_faithfulness",
                verdict="reject",
            ),
        ],
    )
    invalidated_proof = result_record(
        result_id="result:invalidated-proof",
        kind="proof",
        outcome="established",
        evidence_records=[
            evidence("evidence:invalidated-kernel", "kernel_check"),
            evidence("evidence:invalidated-faithfulness", "statement_faithfulness"),
            evidence(
                "evidence:invalidation-review",
                "human_review",
                verdict="reject",
                invalidates=["evidence:invalidated-kernel"],
            ),
        ],
    )

    same_generator_proof = result_record(
        result_id="result:same-generator-proof",
        kind="proof",
        outcome="established",
        evidence_records=[
            {
                **evidence("evidence:same-generator-review", "human_review"),
                "verifier": "candidate-generator",
            },
            evidence("evidence:same-generator-faithfulness", "statement_faithfulness"),
        ],
    )

    derived = validator.derive_solution_ids(
        [
            valid_proof,
            valid_counterexample,
            finite_evidence,
            false_numeric_solution,
            self_reviewed_proof,
            unfaithful_formalization,
            invalidated_proof,
            same_generator_proof,
        ],
        attempts_by_id,
    )
    assert derived == ["result:valid-counterexample", "result:valid-proof"]

    errors: list[str] = []
    validator.validate_cross_references(
        [{"problem_id": "problem:test", "sources": []}],
        {"problem:test"},
        [
            {
                "attempt_id": "attempt:test",
                "problem_id": "problem:test",
                "generator": "candidate-generator",
                "lifecycle": "completed",
                "completed_at": "2026-08-13T00:00:00Z",
            }
        ],
        {"attempt:test"},
        [
            false_numeric_solution,
            self_reviewed_proof,
            unfaithful_formalization,
            invalidated_proof,
            same_generator_proof,
        ],
        errors,
    )
    assert any("不能成为原问题的完整结论" in error for error in errors)
    assert any("缺少独立直接验证" in error for error in errors)
    assert sum("缺少独立直接验证" in error for error in errors) >= 3
    assert any("verifier 不能等于 Attempt.generator" in error for error in errors)

    print(
        "研究空间晋升规则回归测试通过：有限证据、自我审查、失真形式化和失效证据均未进入解库。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
