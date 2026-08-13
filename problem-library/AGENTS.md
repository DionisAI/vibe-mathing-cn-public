# Problem Library Agent Guide

本目录是公开数学问题目录的本地、可重建镜像。`manifest.json` 是抓取批次和完整性真相源；`records/problems.jsonl` 是查询与研究路由入口；`raw/` 只保存来源响应，不接受人工编辑。

## 目录结构

```text
problem-library/
├── AGENTS.md                 # 数据边界与维护规则
├── README.md                 # 数据范围、许可和使用方法
├── COMPLETION_EXEMPLAR.md    # 本次完成方法与复用边界（人读）
├── COMPLETION_EXEMPLAR.json  # 可重算证据绑定的机器契约
├── RETROSPECTIVE.md          # 项目内复盘草稿，不是全局 canonical record
├── REUSE_SAMPLING.json       # 主要任务复用采样决策
├── AUDIT_CASE_SAMPLING.md    # 缺陷修复后的审计案例采样判定
├── manifest.json             # 批次、来源、计数、哈希与覆盖率
├── schema/
│   ├── problem.schema.json   # 单条来源记录契约
│   └── canonical-problem.schema.json # 规范化研究问题契约
├── raw/
│   ├── wikipedia/            # MediaWiki API 原始 JSON
│   └── unsolvedmath/         # 来源发现证据与 109 个公开目录页 HTML 快照
├── records/
│   ├── problems.jsonl        # 两个来源的统一记录流
│   └── canonical-problems.jsonl # 经确认的稳定研究问题
└── indexes/
    ├── catalog.json          # 总量、来源、状态与分类计数
    ├── by-category.json      # 分类到记录 ID 的倒排索引
    └── by-source.json        # 来源到记录 ID 的倒排索引
```

## 边界与依赖

- 上游：Wikipedia MediaWiki API 与 UnsolvedMath 公开目录分页。
- 下游：`scripts/query_problem_library.py`、研究选题、来源核验和后续去重/补全流程。
- Wikipedia 记录继承 CC BY-SA 4.0，必须保留来源、版本和归属。
- UnsolvedMath 未发现公开许可声明；只规范化目录事实与简短卡片摘要，不镜像详情正文。
- UnsolvedMath 来源数据、原始快照、manifest 与派生索引只留本地，不进入公开 Git；需要时通过抓取器重建。
- `raw/` 是证据缓存，不是可编辑知识；刷新只能运行抓取脚本。
- UnsolvedMath 的公开 ID/详情 URL 存在一对多冲突，不得作为主键；本地 ID 由卡片内容指纹生成，冲突组必须进入 manifest。
- 来源记录不能直接作为 canonical Problem；归一化问题必须有版本化陈述和稳定来源 URL，本地来源记录存在时再校验其 ID。
- 任何“完整”声明必须同时满足：目录声明总数、解析总数、本地唯一 ID、源 ID 冲突账本、所有原始页哈希和索引一致性全部通过。

## 维护命令

```bash
python3 scripts/fetch_problem_library.py
python3 scripts/fetch_problem_library.py --refresh
python3 scripts/validate_problem_library.py
python3 scripts/test_problem_library.py
python3 scripts/query_problem_library.py --text riemann --limit 10
```

新增或改变来源适配器时，先保存可复现的代表性结构证据，再修改解析器；结构漂移必须 fail-closed，禁止用空字段或旧缓存伪装成功。
