#!/usr/bin/env python3
"""Exact finite budgets for the shifted-Hankel lifting theorem.

Bounds are conditional on the supplied anchor intervals and full-tail mass.
No root-existence, completeness, or global positivity flag is manufactured.
"""
from __future__ import annotations
from fractions import Fraction as F

MAX_DIMENSION = 10
MAX_SHIFT = 64
MAX_INPUT_BITS = 512


def rational(x):
    """Accept bounded exact rationals, never binary floats or booleans."""
    if type(x) not in (int, F):
        raise ValueError('exact rational required')
    x = F(x)
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_INPUT_BITS:
        raise ValueError('rational input exceeds bit budget')
    return x


def anchor_budget(intervals, radius, mass):
    """Return c_j, alpha_j with b_k=sum c_j alpha_j^k.

    Each Lagrange basis factor is bounded on the entire complex radius disk.
    Overlapping anchor intervals and a missing strict spectral gap fail closed.
    """
    if not isinstance(intervals, (list, tuple)) or not 1 <= len(intervals) <= MAX_DIMENSION:
        raise ValueError('anchor count outside [1,10]')
    r, S = rational(radius), rational(mass)
    if r <= 0 or S < 0:
        raise ValueError('positive radius and nonnegative full-tail mass required')
    boxes = []
    for item in intervals:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError('two endpoints required')
        lo, hi = map(rational, item)
        if not r < lo <= hi:
            raise ValueError('invalid interval or absent strict spectral gap')
        boxes.append((lo, hi))
    for j, (lo, hi) in enumerate(boxes):
        for low, high in boxes[:j]:
            if not (hi < low or high < lo):
                raise ValueError('anchor intervals overlap or touch')
    cs, alphas, bounds = [], [], []
    for j, (lo, hi) in enumerate(boxes):
        M = F(1)
        for l, (low, high) in enumerate(boxes):
            if l == j:
                continue
            gap = max(lo - high, low - hi)
            M *= (r + high) / gap
        cs.append(S * M * M / lo)
        alphas.append(r / lo)
        bounds.append(M)
    return cs, alphas, bounds


def budget(cs, alphas, k):
    """Evaluate the exact nonnegative geometric envelope at one bounded shift."""
    if type(k) is not int or not 0 <= k <= MAX_SHIFT:
        raise ValueError('shift outside [0,64]')
    if not 1 <= len(cs) == len(alphas) <= MAX_DIMENSION:
        raise ValueError('incompatible budget dimensions')
    for c, a in zip(cs, alphas):
        if type(c) not in (int,F) or type(a) not in (int,F) or c < 0 or not 0 <= a < 1:
            raise ValueError('invalid nonnegative contracting budget')
    return sum((F(c) * F(a)**k for c,a in zip(cs,alphas)), F(0))


def first_certified_shift(cs, alphas, maximum=MAX_SHIFT):
    """Find a sufficient K; exhausting the budget is inconclusive, not a refutation."""
    if type(maximum) is not int or not 0 <= maximum <= MAX_SHIFT:
        raise ValueError('invalid search budget')
    for k in range(maximum+1):
        if budget(cs, alphas, k) < 1:
            return k
    return None


def grid_outer(lo, hi, bits=64):
    """Outward round rational endpoints, retaining their exact enclosure."""
    lo,hi=F(lo),F(hi)
    if lo>hi or type(bits) is not int or not 1<=bits<=128:
        raise ValueError('invalid grid enclosure')
    scale=1<<bits
    return F((lo*scale).__floor__(),scale),F((hi*scale).__ceil__(),scale)


def positive_ldl(matrix):
    """Symmetric exact/ball Schur elimination; every pivot must be strictly positive."""
    d=len(matrix)
    if not 1<=d<=MAX_DIMENSION or any(len(row)!=d for row in matrix):
        raise ValueError('bounded nonempty square matrix required')
    for i in range(d):
        for j in range(i):
            if not(matrix[i][j] is matrix[j][i] or matrix[i][j]==matrix[j][i]):
                raise ValueError('symmetry must be exact, not interval overlap')
    a=[list(row) for row in matrix]; out=[]
    for k in range(d):
        pivot=a[k][k]
        if not pivot>0:
            raise ArithmeticError('nonpositive or uncertain Schur pivot')
        out.append(pivot)
        for i in range(k+1,d):
            for j in range(i,d):
                v=a[i][j]-a[i][k]*a[j][k]/pivot
                a[i][j]=v;a[j][i]=v
    return out
