# 本地数学问题库

这里保存两个公开目录的可追溯快照与统一记录：

- [Wikipedia: List of unsolved problems in mathematics](https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics)
- [UnsolvedMath: Mathematics Problem Archive](https://www.unsolvedmath.com/problems)

## 数据范围

- Wikipedia：官方 MediaWiki API 页面版本中，`Unsolved problems` 与 `Problems solved since 1995` 两个区间的直接列表项。
- UnsolvedMath：`/problems` 全部分页中的服务端目录卡片；包含 ID、标题、状态、难度、分类、简短摘要和详情 URL。
- 不抓评论、用户资料、登录后内容、附件或 UnsolvedMath 详情正文。

“完整”只表示当前抓取批次覆盖了来源目录声明的全部条目，不表示问题陈述在数学意义上完备，也不表示两个来源覆盖了世界上所有未解问题。

公开 Git 仓库不分发 UnsolvedMath 未明确授权的目录内容，也不分发动态网页快照。`raw/`、派生 `problems.jsonl`、manifest 和索引保持本地忽略，可由抓取器重建；仓库只版本化抓取代码、schema 和经审查的 canonical Problem。

## 许可与归属

- Wikipedia 内容按其 API 返回的 CC BY-SA 4.0 使用；每条记录和批次清单保留页面版本、许可 URL 与归属。
- UnsolvedMath 未在公开页面、`robots.txt` 或 `sitemap.xml` 提供可识别的许可/抓取清单；本库保留来源链接，只保存公开目录中的事实字段和短摘要。详情页内容仍以原站为准。

## 重建与查询

```bash
# 首次抓取或使用现有缓存重建规范化数据
python3 scripts/fetch_problem_library.py

# 明确刷新全部网络快照
python3 scripts/fetch_problem_library.py --refresh

# 离线完整性验证
python3 scripts/validate_problem_library.py
python3 scripts/test_problem_library.py

# 查询
python3 scripts/query_problem_library.py --source unsolvedmath --category "Number Theory" --limit 20
python3 scripts/query_problem_library.py --text "Riemann" --json
```

`manifest.json` 记录来源总数、实际解析数、原始文件 SHA-256、Wikipedia revision 和各分页实际抓取时间。`raw/unsolvedmath/discovery.json` 保存 `robots.txt` / `sitemap.xml` 的状态、观察时间和响应哈希。抓取器默认复用已存在的原始缓存；只有 `--refresh` 会重新发起网络请求。

### 来源身份异常

UnsolvedMath 当前目录中存在同一公开 ID/详情 URL 对应不同标题的情况。因此：

- `source_native_id` 只作为来源展示字段，不具有唯一性保证；
- 本地 `id` 由来源 ID 与卡片内容指纹生成；完全相同的重复行再追加出现序号；
- 不静默去重，所有目录行都保留，冲突组和超额行数写入 `manifest.json` 的 `identity_anomalies`。

## 数据模型

单条记录契约见 `schema/problem.schema.json`。关键语义：

- `record_scope=list_item`：Wikipedia 列表项。
- `record_scope=listing_card`：UnsolvedMath 目录卡片，不是详情全文。
- `statement_excerpt`：来源目录中用于识别问题的陈述或短摘要。
- `source_revision`：来源支持时保存不可歧义的版本标识；UnsolvedMath 当前没有公开 revision ID，因此为 `null`。

来源记录与规范化问题严格分离：

- `records/problems.jsonl`：外部目录中的来源观察，允许重复、冲突和不完整陈述；
- `records/canonical-problems.jsonl`：人工或受审流程确认后的稳定研究问题，必须携带稳定来源 URL；本地来源记录存在时同时保存其 ID；
- `schema/canonical-problem.schema.json`：canonical Problem 的机器契约。

当前 canonical problems 为空，表示归一化工作尚未用真实问题校准，不表示来源库为空。
