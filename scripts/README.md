# Scripts

- `sync_supply_chain.py`：按 lockfile 幂等拉取、固定和检查 Git 上游。
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
- `test_research_spaces.py`：用负例证明有限证据、自我审查和失真形式化不能进入解库。
- `check.sh`：CI 与本地共用的可移植质量门；任一子检查失败即非零退出。

所有脚本只写本项目范围；失败必须非零退出并打印明确原因。
