# Research Space Agent Guide

本目录是数学研究尝试的真相源。`records/attempts.jsonl` 记录研究活动；`schema/attempt.schema.json` 定义机器契约。

## 目录结构

```text
research/
├── AGENTS.md
├── README.md
├── verifiers.json             # generator/verifier 信任域与能力注册表
├── artifacts/                 # 真实 verifier 输出与可重算回执
├── runs/                      # 可恢复运行 checkpoint（本地忽略）
├── schema/
│   ├── attempt.schema.json
│   ├── evidence-receipt.schema.json
│   ├── run-state.schema.json
│   └── verifier-registry.schema.json
└── records/attempts.jsonl
```

## 职责与依赖

- 上游：规范化 `Problem`、文献目录和项目数学 skills。
- 下游：`result-library/records/results.jsonl` 中引用当前 Attempt 的候选成果。
- 不把尝试完成等同于问题解决；`lifecycle=completed` 只表示本次活动停止。
- `generator` 记录候选生成主体；解库所依赖的独立证据不得由同一主体签发。
- 独立性从 `verifiers.json` 的 trust domain 派生；Result 自报布尔值没有通过权。
- `artifacts/` 是证据可信根；locator 逃逸、symlink、文件缺失或现场摘要不符一律拒绝。
- `.store.lock`、事务日志与 `runs/` 属于可恢复 runtime，不是数学事实源。
- 输入、声明和产物使用稳定 ID 或仓库相对路径；不得写入凭据、私有材料或伪造日志。
- 新增、删除或移动文件时同步维护本文件与 README。

## 验证

```bash
python3 scripts/validate_research_spaces.py
```
