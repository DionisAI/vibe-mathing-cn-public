---
id: GOV-TOOLCHAIN-MODEL
type: context
status: current
owner: engineering
created: 2026-08-13
last_reviewed: 2026-08-13
review_cycle: P90D
---

# Toolchain Model

本项目优先复用 Git、GitHub Actions、JSON Schema、Python 数学库和 proof assistant；自研代码只连接来源、研究记录、验证与派生索引。

## 成熟工具优先

- Git/GitHub Actions 管版本和持续验证。
- JSON Schema 管结构契约，Python 脚本只做跨记录不变量和胶水编排。
- SymPy、NumPy、SciPy、mpmath 管计算，不自研通用代数或数值内核。
- Lean/Mathlib 启用后管理形式化证明，不自研 proof kernel。

## 项目命令

| 场景 | 命令 | 边界 |
|---|---|---|
| 安装依赖 | `python3 -m pip install -r requirements.txt` | 使用固定 Python 包版本 |
| 可移植质量门 | `make check` | CI 和本地共用；不要求 ignored 材料 |
| 本机完整门禁 | `make check-full` | 额外校验上游缓存、原始网页和电子书摘要 |
| 研究空间验证 | `python3 scripts/validate_research_spaces.py` | 只读校验记录与解库派生一致性 |
| 刷新解库索引 | `python3 scripts/validate_research_spaces.py --write-index` | 只更新派生索引，随后仍需只读校验 |
| 查询来源问题 | `python3 scripts/query_problem_library.py --text <query>` | 查询来源记录，不自动归一化 |
| 刷新问题来源 | `python3 scripts/fetch_problem_library.py --refresh` | 网络操作；不在 CI 中运行 |
| 同步供应链 | `make sync-supply-chain` | 网络操作；不在 CI 中运行 |
| GitHub CI | `.github/workflows/ci.yml` | Python 3.12、最小只读权限、15 分钟超时 |

## 依赖边界

- `requirements.txt` 是 CI 与本地可移植质量门的 Python 依赖真相源。
- `requirements-problem-library.txt` 保留为抓取器的窄依赖清单；新增公共依赖必须同步评估两者职责。
- `vendor/upstream/`、`problem-library/raw/`、`literature/files/` 是本地忽略材料，不得成为 `make check` 的隐式依赖。
- proof assistant 尚未安装；Lean/Mathlib 启用前任何 `kernel-checked` 状态必须 fail-closed。

## 性能与成本

- 可移植校验对记录数线性扫描，当前约 6012 条来源记录，适合每次 CI 运行。
- `make check-full` 会读取约 1 GiB 电子书并校验哈希，只适合本地加强门禁，不放入普通 CI。
- 问题抓取为外部网络 I/O，必须显式刷新、有限重试和限速，不作为提交门禁。

## 禁止或谨慎使用

- 禁止用 CI 重新抓取动态网页后覆盖版本化记录。
- 禁止把本地 PDF、凭据、上游 Git pack 或原始网站快照上传到公开仓库。
- 禁止手工修改 `solutions.json` 制造未通过 Result 验证的解。
- 禁止新增无 owner、无验证命令、无错误语义的长期脚本。

## 回滚

工具链或 CI 变更通过普通 Git revert 回滚。派生索引可从 `results.jsonl` 重算；本地缓存与电子书不受 Git 回滚影响。

## 工具链变更流程

1. 先证明现有工具与项目脚本不能满足当前需求。
2. 明确版本、来源、owner、许可、安全权限、性能成本和退出路径。
3. 同步 `requirements.txt`、Makefile、CI、脚本文档与本模型。
4. 在干净环境运行 `make check`，本机材料相关变更再运行 `make check-full`。
5. 用普通 Git revert 回滚；禁止为工具链升级改写已发布历史。
