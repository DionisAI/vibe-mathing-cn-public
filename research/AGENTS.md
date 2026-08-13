# Research Space Agent Guide

本目录是数学研究尝试的真相源。`records/attempts.jsonl` 记录研究活动；`schema/attempt.schema.json` 定义机器契约。

## 目录结构

```text
research/
├── AGENTS.md
├── README.md
├── schema/attempt.schema.json
└── records/attempts.jsonl
```

## 职责与依赖

- 上游：规范化 `Problem`、文献目录和项目数学 skills。
- 下游：`result-library/records/results.jsonl` 中引用当前 Attempt 的候选成果。
- 不把尝试完成等同于问题解决；`lifecycle=completed` 只表示本次活动停止。
- `generator` 记录候选生成主体；解库所依赖的独立证据不得由同一主体签发。
- 输入、声明和产物使用稳定 ID 或仓库相对路径；不得写入凭据、私有材料或伪造日志。
- 新增、删除或移动文件时同步维护本文件与 README。

## 验证

```bash
python3 scripts/validate_research_spaces.py
```
