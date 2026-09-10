# Verification Fixtures Agent Guide

本目录保存可重复、无外部业务数据的验证样例；fixture 只证明工具链和信任边界，不进入真实问题库。

## 目录结构

```text
fixtures/
├── AGENTS.md
├── HHT_COFINAL.md            # Four fixed witnesses, dimension-cofinal criterion and eventual111 budget
├── HHT_SIGN_BLOCKS.md         # Ordered positive compression: unbounded terms, bounded sign changes
├── HHT_TOTAL.md              # 稀疏多项式正性、经典 TP10 推论与下一维数缺口
├── HHT_SHIFTS.md             # 真实 ξ 固定十阶的全部移位：插值尾界与验证范围
├── HHT005.md                 # 固定 ξ 系数/根覆盖认证与完整无限和判据的验证范围
├── XI_STRIP.md               # HHT-004：真实零点映射、零移位负尾界与未完成义务
├── xi_strip.py               # 精确区间和条件性高度尾界；不认证根表
├── HEAT_HANKEL.md             # 合成热迹/Hankel 反例族的证明草稿与边界
├── HANKEL_TAIL.md             # HHT-003：无限谱计数尾界与完整负证书
├── hankel_tail.py             # 有理方向/算子尾界与条件性区间判断
├── HANKEL_INERTIA.md          # HHT-002：惯性计数与任意移位的低阶盲区
├── hankel_inertia.py          # 精确 1x1/2x2 惯性消元及有理充分条件
├── heat_hankel.py             # 标准库精确算术，无 canonical ledger 写入
├── lean-proof/                # 固定 Lean/Mathlib 的最小 kernel 垂直链
├── smt-lra/                   # 有界 SMT/LRA adapter 与攻击样例
└── sympy-counterexample/      # 可经 CLI 注册的确定性反例 Problem
```

## 边界

- 上游：官方 Lean、Mathlib 固定版本。
- 下游：`scripts/vibe_mathing/lean.py`、`scripts/vibe_mathing/smt.py`、`scripts/test_heat_hankel.py`、`scripts/test_hankel_inertia.py`、`scripts/test_hankel_tail.py`、`scripts/test_xi_strip.py`、`scripts/check_hht_lean.py`、`scripts/certify_xi_prefix.py`、`scripts/check_hht_infinite.py`、`scripts/certify_xi_shifts.py`、`scripts/check_hht_shifts.py`、`scripts/certify_xi_sparse.py`、`scripts/check_hht_total.py`、`scripts/hht_sign_blocks.py`、`scripts/certify_xi_sign_blocks.py`、`scripts/check_hht_sign_blocks.py` 、`scripts/test_hht_cofinal.py`、`scripts/certify_xi_cofinal.py`、`scripts/check_hht_cofinal.py` 及对应测试。
- 禁止 `sorry`、`admit`、`unsafe`；变更定理陈述时必须同步陈述忠实性契约和 axiom audit。
- fixture 不得引用本机绝对路径、凭据、私有材料或网络动态内容；fixture PASS 不得创建 Problem、Attempt、Result 或 Solution。
