# Project Codex Guide

本目录只保存 Vibe Mathing 的项目级 Codex 配置。它不反向修改用户级 `$CODEX_HOME/skills`，也不直接激活 `vendor/upstream/` 中的第三方 skills。

## 目录结构

```text
.codex/
├── AGENTS.md
└── skills/
    ├── vibe-mathing-router/
    ├── math-discovery/
    ├── math-derivation/
    ├── math-computation/
    ├── math-proof/
    └── math-formalization/
```

## 依赖方向

```text
vibe-mathing-router
  -> exactly one owner skill

math-discovery -> math-derivation | math-proof
math-derivation -> math-computation | math-proof
math-computation -> evidence only
math-proof -> math-formalization when available
math-formalization -> Lean kernel evidence
```

每个 skill 必须包含 `SKILL.md`、`VERSION`、`CHANGELOG.md` 和来源/压力测试参考。禁止把上游安装器、全局配置写入器、旧 MCP 名称或隐含私有 workspace 直接复制进 active skill。
