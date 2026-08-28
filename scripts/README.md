# Scripts

- `validate_public_boundary.py`：验证公开 origin、禁止路径、符号链接、敏感内容模式和不可发布文件类型，拒绝私密研究或运行资产进入公开 Git 树。
- `test_validate_public_boundary.py`：攻击公开路径和敏感内容门禁，并验证未知输入 fail-closed。
- `sync_supply_chain.py`：按 lockfile 幂等同步并检查 Git 上游、本机 auto-research 完整镜像和审计快照。
- `validate_project.py`：校验 active skill 结构、来源映射和禁止依赖。
- `smoke_math.py`：验证当前 SymPy/mpmath 数学计算后端。
- `fetch_problem_library.py`：限速抓取两个公开问题目录，保存原始快照并重建 JSONL 与索引。
- `validate_problem_library.py`：离线校验条目覆盖率、唯一性、许可归属、缓存哈希和索引一致性。
- `test_problem_library.py`：从原始快照重算 Wikipedia 覆盖和 UnsolvedMath 源 ID 冲突回归事实。
- `query_problem_library.py`：按来源、状态、分类或文本查询规范化问题记录。
- `validate_literature.py`：校验电子书 Work/Edition/File 目录、ISBN、引用和文件摘要。
- `validate_portable_problem_library.py`：校验进入 Git 的问题记录、schema、manifest 与索引，不要求原始网页。
- `validate_portable_literature.py`：校验进入 Git 的文献目录、schema 与引用，不要求本地电子书。
- `validate_research_spaces.py`：校验 Problem/Attempt/Result 引用、二维状态和完整解派生索引。
- `test_research_spaces.py`：用真实回执正例和攻击性反例校验解库晋升。
- `test_trusted_evidence.py` / `test_evidence_attacks.py`：证明伪 locator/hash、路径逃逸、symlink、自验证与越权能力全部 fail-closed。
- `test_research_store.py`：验证 JSONL 唯一 writer、并发幂等与 WAL 崩溃恢复。
- `vibe_mathing_cli.py`：统一 `register-problem/run/resume/verify/status/cancel` 单机入口。
- `test_vibe_mathing_runtime.py`：验证状态转换、重试、超时和输出预算。
- `test_vibe_mathing_pipeline.py`：运行可恢复、可失效的确定性 SymPy CLI 垂直链。
- `test_lean_pipeline.py`：运行固定 Lean/Mathlib kernel、逃逸、公理和陈述忠实性链。
- `pipeline_maturity_audit.py`：现场执行 required capabilities，严格模式只在全部通过时输出 100/100。
- `check.sh`：CI 与本地共用的可移植质量门；任一子检查失败即非零退出。

所有脚本只写本项目范围；失败必须非零退出并打印明确原因。
