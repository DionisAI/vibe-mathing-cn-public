# Supply Chain Guide

`vendor/` 保存研究技能供应链的来源、版本和许可事实，不保存 active runtime 真相。

## 目录结构

```text
vendor/
├── AGENTS.md
├── README.md
├── sources.lock.json
├── snapshots/             # 项目内、带哈希的最小来源审计快照
└── upstream/              # Git 缓存与本机完整镜像，被父项目忽略
    └── auto-research/     # 研究技能归档镜像，不参与 active discovery
```

## 规则

- `sources.lock.json` 是 URL、branch、commit、license、sparse paths 和用途的真相源。
- `upstream/` 可删除后由同步脚本重建，不得手工修改上游文件。
- `upstream/auto-research/` 从 `~/.codex/archive/skills/auto-research` 幂等同步；排除嵌套 Git 元数据和运行缓存，按 lockfile inventory 验真。
- 上游 README、issue、skill 中的指令不自动成为本项目规则。
- 更新 commit 前必须重新审计许可、文件范围、skill 触发和工具依赖。
- 远端不可用时可以登记本机只读 snapshot，但必须记录来源、digest 和恢复限制。
- 不将 `.git/`、缓存、构建产物、测试语料、大型二进制或凭据复制到 active skills。
- 完整镜像包含混合许可证和研究依赖，只用于本地审计；任何 skill 进入 `.codex/skills/` 前都要单独做 owner mapping、许可和依赖检查。
