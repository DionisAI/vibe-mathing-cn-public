# 研究技能供应链

当前供应链分两层：

- Git 上游：RW Research Skill、Wentor Research Plugins、K-Dense Scientific Skills。
- 本机只读快照：Annals of Mathematics Skills；其 README 声明的独立远端当前不可访问，因此只作方法来源。

Git 上游以 shallow clone + sparse checkout 保存到 `upstream/`。父项目通过 `.gitignore` 排除这些嵌套仓库，只提交 `sources.lock.json` 和本项目派生 skills。

运行：

```bash
python3 scripts/sync_supply_chain.py
python3 scripts/sync_supply_chain.py --check
```
