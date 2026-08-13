# Changelog

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
