# Review：供应链与项目级数学研究 Skills

## Verdict

`PASS`：本轮复制、拉取、隔离和 active skill 构建满足当前任务范围。公开再分发前仍需处理 `unknown-local` 许可项；Lean 形式化能力保持 calibration。

## Scope

- correctness：同步脚本、lockfile、hash、失败语义和数学 smoke。
- security/repo hygiene：凭据扫描、嵌套 Git、生成物和大文件边界。
- architecture：active skills、供应链缓存与来源快照的依赖方向。
- performance：首次拉取体积、重复运行成本和校验复杂度。
- completion verification：当前输入绑定的同步、strict skill 和 smoke 证据。

## Findings

无 BLOCK/WARN 级实现 finding。

## Known Limits

- `kdense-scientific-skills` shallow clone 的 Git pack 约 220 MiB；实际 sparse 工作树约 1.2 MiB。它位于可重建且被忽略的 `vendor/upstream/`，不进入父项目交付。
- `local-formula-derivation` 与 `local-proof-writer` 缺少可确认的独立许可，只作为本机内部来源快照，禁止在未补充许可证据时单独再分发。
- 本机没有 Lean/elan/lake，`math-formalization` 只允许生成形式化计划，不能声明 `kernel-checked`。
- Annals 声明的独立远端在 2026-08-13 返回 not found；项目保存了三个实际吸收文件及原 MIT 许可的哈希快照。

## Verification

```bash
python3 scripts/sync_supply_chain.py --check
python3 scripts/validate_project.py
python3 scripts/smoke_math.py
for d in .codex/skills/*; do
  "$CODEX_HOME/skills/auto-skill/scripts/validate-skill.sh" "$d" --strict
done
```

秘密扫描未发现常见私钥、GitHub token、AWS access key 或硬编码密码模式。当前审查是同一执行主体的确定性复核，不冒充独立 reviewer provenance。

## Efficiency

- `sync_supply_chain.py --check` 对仓库数量和锁定文件数量线性扫描；当前 3 个 Git 仓库、6 个 snapshot 文件，不是 hot path。
- 每个 Git 仓库只做常数次 `git status/rev-parse` 与许可证 hash；不会遍历 220 MiB pack 内容。
- `smoke_math.py` 是常数规模测试；80 位积分只用于门禁，运行小于一秒。
- 当前不值得增加缓存数据库、并发调度或通用依赖管理框架。

---

# Review：本地数学问题库

## Verdict

`PASS`：两个指定来源的条目级目录已完整落地，当前快照、规范化记录、索引、许可边界和离线重建证据一致。该结论不扩张为 UnsolvedMath 详情全文镜像。

## Scope

- correctness / contract：分页覆盖、Wikipedia 章节解析、schema、状态和字段语义。
- reliability：超时、有限重试、限速、原子写入、缓存复用和结构漂移 fail-closed。
- repo hygiene / licensing：原始缓存隔离、Wikipedia 归属、UnsolvedMath 未知许可边界和秘密扫描。
- performance：109 页串行网络成本、DOM 解析复杂度、JSONL/索引内存与离线门禁耗时。
- completion verification：从原始快照重算关键事实，不接受 manifest 自报替代证明。

## Findings

无 BLOCK/WARN 级实现 finding。

来源质量 finding 已被模型化而非隐藏：UnsolvedMath 的 5,426 个目录行只有 5,375 个不同公开 ID，包含 35 个冲突 ID 组和 51 个超额行。本地使用卡片内容指纹 ID，完整保留冲突行并写入 `manifest.json`。

## Known Limits

- “完整”仅指当前批次覆盖 Wikipedia 两个目标章节的直接列表项，以及 UnsolvedMath 目录声明的 109 页/5,426 行。
- UnsolvedMath 未公开可识别的内容许可，且详情正文由客户端加载；本库只保存公开目录事实、短摘要和详情 URL。
- Wikipedia 是动态页面；刷新后条目数变化是允许的，但 API revision、原始哈希和派生计数必须重新一致。
- 当前审查是同一执行主体的确定性复核，不冒充外部独立 reviewer provenance。

## Verification

```bash
python3 -m py_compile scripts/fetch_problem_library.py scripts/validate_problem_library.py scripts/test_problem_library.py scripts/query_problem_library.py
python3 scripts/validate_problem_library.py
python3 scripts/test_problem_library.py
python3 scripts/query_problem_library.py --text Riemann --limit 2
python3 -B scripts/sync_supply_chain.py --check
python3 -B scripts/validate_project.py
python3 -B scripts/smoke_math.py
```

最终新鲜结果：总计 6,012 条；Wikipedia 586 条；UnsolvedMath 5,426/5,426 条、109/109 页；全部 6,012 条通过 JSON Schema、唯一本地 ID、原始哈希和索引一致性门禁。

## Efficiency

- 网络刷新为 `O(P)` 次请求，`P=109` 个 UnsolvedMath 分页，另加 Wikipedia API 与来源发现探测；串行限速、显式超时、最多 3 次退避重试。
- 解析成本为 `O(B + N)`，`B` 是约 22 MB 原始响应，`N=6,012` 条记录；索引和校验内存为 `O(N)`。
- 离线完整校验实测约 0.75 秒；整个问题库约 27 MB，不是运行时 hot path。
- 立即值得做的优化已经完成：原始缓存复用和原子覆盖。当前不值得引入数据库、异步抓取或并行连接；若来源增长到 100 倍，再评估流式索引和并发上限。

## Rollback

删除本轮新增的 `problem-library/`、四个 problem-library 脚本和 `requirements-problem-library.txt`，并撤销根 README/AGENTS/CHANGELOG/.gitignore 与 `scripts/README.md` 的对应条目即可；不涉及数据库、远端仓库或外部写操作。

---

# Review：非可信生成器与受信验证链

## Verdict

`PASS`：README、Problem/Attempt/Result 契约、完整解派生谓词、负例和治理文档已使用同一模型。该结论来自同一执行主体的确定性复核，不冒充外部独立 reviewer provenance。

## Findings

发布前审查发现并修复两项 BLOCK：Result 原可引用不同 Problem 的 Attempt；`independent=true` 原未与 Attempt.generator 交叉核对。当前派生函数直接检查同 Problem、不同主体、可复查 SHA-256、独立直接验证、statement faithfulness 和证据失效账本。

## Verification

```bash
python3 scripts/test_research_spaces.py
python3 scripts/validate_research_spaces.py
make check
make check-full
python3 governance/tools/validate_governance_package.py --project-root . --strict
python3 governance/tools/governance_health_report.py --project-root . --strict
```

负例覆盖有限数值证据、自我审查、陈述失真、关键证据失效和同生成者验证。

公开克隆等价验证通过：从 Git 暂存树导出的干净副本安装 `requirements.txt` 后运行 `make check`，不依赖 ignored 问题原始页、电子书二进制或供应链缓存。

## Known Limits

- `generator` / `verifier` 是可审计身份字段，不是密码学证明；真正独立 reviewer provenance 仍需外部签名或平台证明。
- 当前没有 Lean/elan/lake，kernel capability 仅有契约，没有真实内核执行证据。
- 当前三张逻辑表为空，下一步需要用可证明、可反驳、开放问题三个垂直样例校准语义。

## Efficiency

校验时间与 Problem、Attempt、Result 及其证据记录总数线性相关，空间复杂度同样为线性；当前不是 hot path。立即引入数据库、缓存或并发会增加所有权面，没有收益。数据达到 10x/100x 后再用基准测试决定是否迁移到带外键和物化视图的数据库。

## Rollback

回滚本次初始提交即可；业务真相源为空，不涉及数据迁移。`solutions.json` 可由 Result 重新派生。

## Remote Evidence

- Repository: `https://github.com/tradecatlabs/vibe-mathing-cn`
- Implementation commit: `33dd5de27c174893c36a0dcd11647822463168e8`
- GitHub Actions: `https://github.com/tradecatlabs/vibe-mathing-cn/actions/runs/31703110676`
- Result: `validate` job PASS on GitHub-hosted Python 3.12.
