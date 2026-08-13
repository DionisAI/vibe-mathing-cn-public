---
id: GOV-PROJECT-OPERATING-MODEL
type: context
status: current
owner: engineering
created: 2026-08-13
last_reviewed: 2026-08-13
review_cycle: P90D
---

# Project Operating Model

本文件是 Vibe Mathing 的项目级操作模型。根 README 面向使用者说明项目，目录 README/AGENTS 管理局部事实，本文件维护跨模块真相源、变更路由和验收边界。

## 项目一句话定义

`vibe-mathing-cn` 是一个用非可信生成器产生候选，再由受信验证链把满足验收谓词的证明或反例派生到解空间的 AI 数学研究工作台。

## 业务模型

- 核心用户：使用 AI 做数学探索、计算、证明和形式化验证的研究者与工程师。
- 核心对象：`Problem`、`Attempt`、`Result`。
- 关键流程：来源记录 → canonical Problem → Attempt → candidate Result → trusted verification gate → solution view。
- 不属于本项目：保证自动解决开放问题、把有限实验当一般证明、把模型自评当独立验证、镜像未获授权的文献全文。

## 技术模型

- 主要运行形态：Git 管理的 Markdown、JSON/JSONL、JSON Schema、Python 校验器和项目级 Codex skills。
- 数据事实源：来源记录在 `problem-library/records/problems.jsonl`；规范化问题在 `canonical-problems.jsonl`；研究与成果分别在 `research/records/` 和 `result-library/records/`。
- 派生视图：`result-library/indexes/solutions.json`，禁止绕过 Result 真相源直接录入。
- 外部依赖：公开问题来源、文献数据库、Python 数学/校验库；上游 skill 版本由 `vendor/sources.lock.json` 固定。
- 主要验证入口：`make check`；本机完整材料加强验证为 `make check-full`。

## 工具链模型

工具链的命令、依赖、CI 边界、成本与回滚以 `context/TOOLCHAIN_MODEL.md` 为准。核心约束是：CI 只消费可版本化资产，本地 ignored 材料只进入 `make check-full`。

## 目录和真相源地图

| 事实类型 | 真相源 | 备注 |
|---|---|---|
| 项目定位与使用入口 | `README.md` | 面向使用者 |
| Agent 运行边界 | `AGENTS.md` | 数学真实性与目录维护规则 |
| 来源问题观察 | `problem-library/records/problems.jsonl` | 不等于 canonical Problem |
| 规范化问题 | `problem-library/records/canonical-problems.jsonl` | 版本化陈述、稳定来源 URL 与可选本地来源记录 ID |
| 研究尝试 | `research/records/attempts.jsonl` | Attempt lifecycle 不表达数学结论 |
| 研究成果 | `result-library/records/results.jsonl` | `outcome × evidence` 二维状态与追加证据账本 |
| 完整解视图 | `result-library/indexes/solutions.json` | 从 Result 派生 |
| 文献书目 | `literature/catalog/*.jsonl` | 电子书二进制保持本地忽略 |
| 研究方法 | `.codex/skills/` | 只保存 active owner skills |
| 供应链版本 | `vendor/sources.lock.json` | URL、commit、许可和导入映射 |
| 项目治理 | `governance/` | 标准、ADR、Gate 和任务证据 |
| CI 入口 | `.github/workflows/ci.yml` | 只运行可移植质量门 |

## 不可违反的边界

1. 来源记录不自动成为 canonical Problem。
2. Attempt 不自动成为 Result，Result 不自动成为 Solution。
3. 数值/符号证据、局部/条件结果和失败路径不能关闭原问题。
4. 完整解必须是 `proof + established` 或 `counterexample + refuted`，并具备当前有效的独立直接验证和 statement faithfulness `accept`。
5. proof assistant 成功只证明形式化陈述，仍需审计其是否忠实表达原问题。
6. 证据能力按集合偏序表达；不得把 outcome 与 numeric/human/kernel 压成单一等级。
7. Result 与 Attempt 必须引用同一个 Problem；独立 verifier 不得等于 Attempt.generator，准入证据必须有可复查摘要。
8. CI 不访问外部来源、不上传本地文献、不修改研究真相源。
9. UnsolvedMath 未明确许可的目录内容只作为本地可重建数据，不进入公开 Git。

## 变更入口

- 改对象字段：同步修改 owner schema、局部 README/AGENTS、校验器与回归测试。
- 改晋升规则：同步修改 Result schema、校验器、负例、GATE-0002 和 ADR。
- 改工具/CI：同步修改 `Makefile`、`scripts/check.sh`、`.github/workflows/ci.yml` 与 `TOOLCHAIN_MODEL.md`。
- 新增目录或重划职责：同步根与目标目录 README/AGENTS、PROJECT-TOPOLOGY 和 module context。

## 验证入口

```bash
make check
make check-full
python3 governance/tools/governance_context_bundle.py --project-root . --task-type docs
```

## 最近一次 review

- 日期：2026-08-13
- 结论：最小研究空间、成果空间、晋升门和可移植 CI 已建立；数学内容仍为空。
- 后续动作：用三个真实垂直样例校准 Problem 归一化与成果晋升，然后实现 `/vibe-mathing` 总控入口。
