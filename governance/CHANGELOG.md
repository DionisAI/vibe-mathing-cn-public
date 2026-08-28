---
id: GOV-CHANGELOG
type: changelog
status: current
owner: engineering
created: 2026-08-13
last_reviewed: 2026-08-29
review_cycle: P90D
---

# 治理包变更记录

- 新增公开仓库发布边界和自包含机器门禁，拒绝私密研究路径、恢复快照、生成物、绝对用户路径、私有网络标识与凭据模式进入公开 Git 树。
- 初始化治理包。
- 记录 Problem → Attempt → Result → 派生解空间的项目操作模型与 ADR-0000。
- Result 采用 `outcome × evidence`，并以偏序能力集和追加失效账本替代单一证据等级。
- 新增 GATE-0002，阻止有限证据、自我审查和陈述失真进入完整解视图。
- 登记 problem-library、research、result-library 模块上下文和可移植/完整两级工具链。
- 发布项目级 `VIBE-MATHING-SPEC v0.1`，把研究闭环压缩为 R1 候选隔离、R2 验证准入、R3 证据守恒；九条候选要求收敛为操作层推论。
