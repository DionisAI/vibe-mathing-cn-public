# HHT 的 Lean 验证范围

**已核实状态：12 条子命题在 GitHub Actions 上实际通过 Lean 4.33.0 编译及逐条依赖审计。**
这只覆盖下表列出的子命题，不覆盖完整解析论证、实际根数据前提或 RH。

- 已检查代码提交：`30bebb87bfbbe82251d8ae7a2845eb3d28bb11e8`。
- 实际 PR 合并测试提交：`98c2f4862f918bc22d448f22fbdc35518b7c8e42`（临时测试对象，PR 未合并）。
- Lean 源码 blob：`540f876875398eb15eabeb7caaca7356506ece68`。
- Lean 实际版本：4.33.0，编译器提交 `d8b18978322de05a8f3dba51ef03cf5461676c17`。
- Mathlib 固定提交：`db584cd6d46c92f209a44c0f1c829460d327499d`。
- [成功运行及日志](https://github.com/DionisAI/vibe-mathing-cn-public/actions/runs/34298451517/job/102300049675)。
- 日志最终输出：`LEAN_SLICES_PASS: 12 theorem audits; not the full analytic theorem or RH.`
- 全部 12 条依赖报告均仅为 `[propext, Classical.choice, Quot.sound]`。
- 同一代码提交的 [完整 CI](https://github.com/DionisAI/vibe-mathing-cn-public/actions/runs/34298451545)
  中 `validate`（含完整 `make check`）和 `production-loop` 均成功。

本次文档更新不改变上述 Lean 源码或验证器。执行历史保留：本地因没有 Lean/lake 而阻断；
远端首轮在全量 Mathlib 导入时读取失败，随后缩小依赖，并修正辅助引理方向、
保留字 binder 和严格战术 linter 报错。没有放宽审计规则、关闭警告或削弱数学陈述。
Python 算术与日志解析器测试不被用来替代这次实际 Lean 运行。

复用此目录原有 Lean 4.33.0 与 lake-manifest.json 固定的 Mathlib。
没有修改已有 VibeMathingFixture、statement-faithfulness 契约、可信 verifier 或数学晋升策略。
`HHTCertificates.lean` 是另外的子命题文件，编译不是原 fixture 的自动默认目标。

在仓库根目录运行：

```bash
# 先按原 fixture README 准备固定依赖；不要运行会漂移版本的 lake update。
(cd fixtures/lean-proof && timeout 900s lake exe cache get)
timeout 300s python3 scripts/check_hht_lean.py
```

另提供 `.github/workflows/hht-lean.yml`，只有读权限，无模型调用、无写 token、无定时任务。
如果仓库 Actions 没有执行此工作流，不能据此宣称检查通过。

## 陈述对应表

| Lean 子命题 | 覆盖的数学内容 | 没有覆盖的内容 |
|---|---|---|
| lambda_norm_sq | 映射坐标的平方模恒等式 | ξ 整性、零点存在性 |
| lambda_im_zero_iff | gamma>0 时虚部为零 iff delta=0 | RH |
| lambda_re_positive | strip 的平方界和 gamma>=1 推出正实部 | 全部零点输入 |
| unshifted_square_identity / unshifted_block_lower | 配方恒等式与 x>0 时的一侧下界 | 无限求和与计数定理 |
| linear_polynomial_block_lower | p(u)=a+b*u 的代入 | 任意次数虚部估计 |
| prefix_tail_negative_transfer | 显式分解、前缀误差与尾界推出负号 | 这些前提是否对真实谱成立 |
| synthetic_negative_margin / conditional_synthetic_negative | HHT-003 有理余量与条件负号转移 | 无限乘积、无限尾界证明 |
| two_node_schur_identity | 两个节点的 Schur 分子恒等式 | 根区间认证 |
| h2_margin_arithmetic / conditional_h2_margin_positive | HHT-004 精确余量与条件不等式 | 全二阶矩阵的真实数据前提 |

共 12 条 theorem。每条都有 `#print axioms`。
runner 要求编译实际成功、每条依赖报告恰好出现一次、依赖仅属于
`propext / Classical.choice / Quot.sound`，并限制时间、内存和输出。
这是源码受控情况下的运行检查，不是独立的 Lean 内核实现，也不代替陈述忠实性审查。

没有把未证明的 ξ 定理作为全局公理加入 Lean。必要的局部数学假设在 theorem 的参数中保留。
对本文件后续修改应同时核对上表，不能为了通过编译削弱声明再冒称验证了原命题。
