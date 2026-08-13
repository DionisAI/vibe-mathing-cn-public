# 研究空间

`research/` 保存从规范化问题出发的一次次研究尝试。它记录做过什么、使用了什么方法、产生了哪些声明和产物；不负责宣布问题已经解决。

## 目录结构

```text
research/
├── AGENTS.md
├── README.md
├── schema/
│   └── attempt.schema.json
└── records/
    └── attempts.jsonl
```

## 边界

- 每个 `Attempt` 必须引用 `problem-library/records/canonical-problems.jsonl` 中的一个问题，并记录候选生成者 `generator`。
- discovery、derivation、computation、proof、formalization 是研究方法，不是完成等级。
- `lifecycle` 只描述尝试的运行状态，不表达数学结论；失败、阻塞和未闭合证明义务可以保存。
- 研究产物要进入成果空间，必须另建 `Result` 并通过验证门。

## 验证

```bash
python3 scripts/validate_research_spaces.py
```
