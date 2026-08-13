---
name: math-computation
description: "可重跑的数学计算与反例实验。用于 SymPy 精确代数/微积分/方程/矩阵、NumPy/SciPy 数值方法、mpmath 高精度交叉检查、OEIS 序列识别、有限范围反例搜索和计算证据记录。"
---

# Math Computation

用成熟计算库生成可重跑证据；计算用于发现、反驳和核对，不越权成为一般性证明。

## When to Use This Skill

- 需要精确化简、求解、积分、极限、级数、矩阵或多项式计算。
- 需要高精度数值交叉检查、参数扫描或有限范围反例搜索。
- 需要识别整数序列、测试猜想小规模实例或生成图表数据。

## Not For / Boundaries

- 浮点相等不是数学恒等；优先 exact arithmetic。
- SymPy 返回结果可能带分支、条件或未求值对象，必须检查。
- 有限枚举“未发现反例”不证明全称命题。
- 大规模矩阵/扫描必须先估算复杂度、内存和停止条件。

## Quick Reference

```python
import sympy as sp
x = sp.symbols("x", real=True)
delta = sp.simplify(lhs - rhs)
status = "symbolically-checked" if delta == 0 else "not-verified"
```

执行记录至少包含：输入表达式、假设、库版本、精确/近似模式、命令或脚本、输出、失败条件、claim level。

性能口径：符号表达式可能发生组合爆炸；矩阵稠密求解通常为 O(n^3)/O(n^2) 内存；批量数值优先 `lambdify`/向量化、稀疏结构和有界采样。

## Examples

### Example 1：恒等式检查
- 输入：`lhs = sin(x)^2 + cos(x)^2`，`rhs = 1`。
- 动作：使用实变量假设和 `trigsimp/simplify`。
- 验收：记录 SymPy 版本与差值；状态最多 `symbolically-checked`。

### Example 2：数值反例
- 输入：带参数的不等式猜想。
- 动作：先定义域，再用确定性网格与边界采样，保存首个反例。
- 验收：找到反例即 `refuted-for-stated-domain`；未找到只报告覆盖范围。

### Example 3：大矩阵
- 输入：求解大型稀疏线性系统。
- 动作：识别稀疏性和条件数，优先 SciPy sparse solver，记录残差。
- 验收：没有构造不必要的稠密副本，报告时间/内存规模变量。

## References

- `references/source-map.md`：CAS、数值方法和 OEIS 来源映射。
- `references/pressure-tests.md`：数值/符号证据越权压力场景。

## Maintenance

- Sources：`wentor-research-plugins` 数学技能、`kdense-scientific-skills` 的 SymPy skill。
- Last updated：2026-08-13。
- Verification：`python3 scripts/smoke_math.py`；库 API 以当前官方文档和实测为准。
