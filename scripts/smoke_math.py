#!/usr/bin/env python3
# 做什么：验证 Vibe Mathing 第一阶段依赖的精确符号计算与高精度数值后端。
# 怎么运行：python3 scripts/smoke_math.py
# 需要什么：Python 3、SymPy 1.14+、mpmath；失败时非零退出。

from __future__ import annotations

import json

import mpmath
import sympy as sp


def main() -> int:
    major_minor = tuple(int(part) for part in sp.__version__.split(".")[:2])
    if major_minor < (1, 14):
        raise RuntimeError(f"SymPy 版本过旧：{sp.__version__}")

    x = sp.symbols("x", real=True)
    identity = sp.trigsimp(sp.sin(x) ** 2 + sp.cos(x) ** 2)
    integral = sp.integrate(sp.exp(-(x**2)), (x, -sp.oo, sp.oo))
    with mpmath.workdps(80):
        numeric = mpmath.quad(
            lambda value: mpmath.exp(-(value**2)),
            [-mpmath.inf, mpmath.inf],
        )
        numeric_error = abs(numeric - mpmath.sqrt(mpmath.pi))

    assert identity == 1
    assert integral == sp.sqrt(sp.pi)
    assert numeric_error < mpmath.mpf("1e-30")

    print(json.dumps({
        "status": "PASS",
        "sympy": sp.__version__,
        "identity": str(identity),
        "gaussian_integral": str(integral),
        "claim_level": "symbolically-checked",
        "kernel_checked": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
