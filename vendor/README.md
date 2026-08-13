# 研究技能供应链

当前供应链分两层：

- Git 上游：RW Research Skill、Wentor Research Plugins、K-Dense Scientific Skills。
- 本机完整镜像：`~/.codex/archive/skills/auto-research` 被复制到 `upstream/auto-research/`，保留 4,170 个 skill 入口，但不参与 active skill 发现。
- 本机最小快照：Annals of Mathematics Skills；其 README 声明的独立远端当前不可访问，因此只作方法来源。

Git 上游以 shallow clone + sparse checkout 保存到 `upstream/`。本机完整镜像排除嵌套 `.git`、Python 缓存和系统垃圾文件，并用文件数、字节数与树摘要验真。父项目通过 `.gitignore` 排除这些供应链缓存，只提交 `sources.lock.json` 和本项目派生 skills。

运行：

```bash
python3 scripts/sync_supply_chain.py
python3 scripts/sync_supply_chain.py --check
```

同步命令是幂等的：本机镜像使用 `rsync --delete --delete-excluded` 与锁定排除规则重建；`--check` 同时比较来源、目标和 lockfile inventory，并拒绝失效或越界符号链接。各子项目许可证互不相同，未完成逐项许可审计前不得整体发布或直接激活。
