---
id: MODCTX-PROBLEM-LIBRARY
type: context
status: current
owner: engineering
created: 2026-08-13
last_reviewed: 2026-08-13
review_cycle: P90D
---

# Problem Library Context

- 职责：保存公开来源观察和经确认的 canonical Problem。
- 真相源：本地可重建的 `records/problems.jsonl` 与公开可版本化的 `records/canonical-problems.jsonl`，两者语义不可混用。
- 上游：Wikipedia、UnsolvedMath；原始响应位于被忽略的 `raw/`。
- 下游：Attempt 只能引用 canonical Problem。
- 核心风险：同名误合并、来源 ID 冲突、不完整摘要冒充精确定理陈述。
- 验证：`python3 scripts/validate_portable_problem_library.py`；具备 raw 时再运行 full validator/test。
