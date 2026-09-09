# Lean/Mathlib 最小验证样例

该 fixture 证明三件事：固定工具链可构建、定理无 `sorry/admit/unsafe`、`#print axioms` 输出可审计。它不证明任何开放数学问题，也不替代陈述忠实性审查。

项目 adapter 从 `PATH` 查找 `lean`，并兼容 elan 官方默认安装目录 `~/.elan/bin`；它从固定 `lake-manifest.json` 构造最小 `LEAN_PATH`，再以 `-j1` 和有界资源运行 Lean。缺少固定依赖缓存时 fail-closed。手工准备缓存时不要执行会移动依赖版本的 `lake update`。

```bash
lake exe cache get
lake --quiet build
lake env lean -j1 VibeMathingFixture.lean
lake env lean -j1 AxiomAudit.lean
```

## HHT 研究子命题

`HHTCertificates.lean` 是独立的形式化切片，范围和已核实执行记录见
[HHT_LEAN.md](HHT_LEAN.md)。从仓库根目录运行 `python3 scripts/check_hht_lean.py`。
这不改变上述原有 fixture 的可信声明或默认构建目标。

`HHTInfinite.lean` 进一步验证真实无限求和下的二阶正性充分条件，
8 条定理已通过固定工具链编译与依赖审计。根覆盖及直接系数认证由独立的 FLINT 计算步骤完成，
不能把特殊函数或全域计数输入也标成 Lean 已验证。
完整范围与可复算证据见 [HHT005.md](../HHT005.md)。
从仓库根运行 `python3 scripts/check_hht_infinite.py`；不改旧准入验证器或默认构建目标。
