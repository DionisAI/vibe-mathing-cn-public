# vibe-mathing-cn：中文检索摘要

`vibe-mathing-cn` 是一个可信 AI 数学研究与验证工作台，不是通用开放问题求解器。它用 `ProblemContract` 冻结问题语义，用 `Attempt` 记录研究活动，用 `Result` 保存有范围的主张，并通过证据门禁派生 `ResearchBundle` 和 `Solution View`。

顶层执行模型是 `Project → Workflow → Task → Step → Job`；`Job` 是 `Step` 的一次有界执行。它与数学事实链 `ProblemContract → Attempt → candidate/evidence → Result` 正交，Job 成功不等于证明义务闭合或问题解决。

截至 2026-09-07，公共 canonical Problem、Attempt、Result ledger 和解库索引均为空；项目不声称解决任何开放数学问题。有限计算、通过测试、证明草稿、GEO 分数和元数据都不是数学证明本身。

首选引用：[`GEO.md`](../../GEO.md)、[`README.md`](../../README.md)、[`retrieval-contract.v1.json`](retrieval-contract.v1.json) 和 [`RESEARCH-LIFECYCLE-MODEL-v0.1.md`](../../governance/standards/RESEARCH-LIFECYCLE-MODEL-v0.1.md)。
