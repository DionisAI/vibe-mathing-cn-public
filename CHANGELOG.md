# Changelog

## 2026-08-13 — 单机可信研究闭环 100/100

- 新增受信 verifier registry、不可覆盖证据回执、现场摘要重算和 append-only 失效语义。
- 新增 `flock + WAL + fsync + os.replace` 原子研究存储、可恢复运行状态机与统一 CLI。
- 新增 SymPy 反例和固定 Lean/Mathlib 两条端到端闭环，以及攻击矩阵、故障恢复、成熟度审计和 CI 门禁。
- 100/100 限定为单机、单 Agent、可信研究闭环；Git 交付、外部 reviewer 签发和分布式高可用仍是独立边界。
- Lean adapter 兼容 elan 官方默认目录，即使非交互 shell 未配置 `~/.elan/bin` 也能确定性发现工具链。
- Lean 冷缓存构建使用 Lake 官方 quiet 模式，保留 2 MiB 输出预算而不让进度日志误触发资源门禁。

## 2026-08-13 — VIBE-MATHING-SPEC v0.1

- 发布三条项目基本法则：候选隔离、验证准入、证据守恒。
- Result 证据能力新增 `axiom_escape_audit` 与 `prior_art_review`。
- kernel 直接验证只有与独立公理/逃逸审计组合时才满足完整解准入。

## 2026-08-13 - 本机 auto-research 完整镜像

- 将 `~/.codex/archive/skills/auto-research` 完整工作树复制到被隔离的 `vendor/upstream/auto-research/`。
- 保留 4,170 个 skill 入口和相关代码、文档与数据，排除嵌套 `.git` 和运行缓存；镜像不自动激活、不整体发布。
- 扩展供应链脚本，以来源、目标、lockfile 三方 inventory 和树摘要提供幂等同步与漂移检查。

## 2026-08-13 - 问题空间到解空间基础框架

- 新增 canonical Problem、Attempt、Result 三个最小机器契约与空真相源。
- 结果状态采用 `outcome × evidence` 二维模型；证据使用能力偏序和可失效追加账本。
- 新增研究空间、成果空间和由 Result 派生的解库索引；有限证据、自我审查和陈述失真不能晋升完整解。
- 新增最小治理包、项目操作模型、架构决策和数学成果晋升 Gate。
- 新增 `make check` / `make check-full` 与 GitHub Actions CI；可移植 CI 不依赖本地电子书、原始网页或上游缓存。

## 2026-08-13 - 数学电子书文献库

- 新增 `literature/` 的 Work/Edition/File/Relation 目录模型和 JSON Schema。
- 将《数学大辞典（第二版）》移动到 ISBN 对象路径，分类为 MSC2020 `00A20` 综合数学辞典。
- 新增文件摘要、ISBN、引用完整性离线校验；电子书二进制明确排除 Git。

## 2026-08-13 - 本地数学问题库

- 新增 `problem-library/`，保存 Wikipedia 与 UnsolvedMath 的原始目录快照、统一问题记录和倒排索引。
- 新增幂等抓取、离线校验与查询脚本；UnsolvedMath 完整性绑定站点声明总数和分页哈希。
- 明确 Wikipedia CC BY-SA 归属以及 UnsolvedMath 未知许可下的“目录字段/短摘要、不镜像详情正文”边界。

## 0.1.0 - 2026-08-13

- 初始化 Vibe Mathing 中文数学研究工作台。
- 新增 6 个项目级 active skills：路由、发现、推导、计算、证明和形式化。
- 拉取并锁定 RW、Wentor、K-Dense 三个上游供应链仓库。
- 保存 Annals 三个证明相关 skill 和两个本机 research skill 的精简快照。
- 新增供应链同步、项目结构校验和 SymPy 数学 smoke 脚本。
- 建立 `conjecture` 到 `kernel-checked` 的证据状态边界。
