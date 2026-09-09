#!/usr/bin/env python3
"""Finite algebra shared by exact tests and the bounded FLINT experiment.

LDL inputs must be symmetric; reused interval objects represent identical
entries, not merely overlapping enclosures. No network or ledger operations.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb

MAX_DIMENSION = 10


def dimension(d: int) -> int:
    """Reject zero, bool and out-of-budget dimensions."""
    if type(d) is not int or not 1 <= d <= MAX_DIMENSION:
        raise ValueError('dimension must be an integer in [1,10]')
    return d


def ldl_polynomials(matrix: list[list]) -> tuple[list[list], list]:
    """Return B=L^-1 and positive pivots D, so B A B^T=diag(D).

All arithmetic is performed in the supplied exact/ball type. An uncertain
pivot raises instead of asserting positive definiteness. No pivot clipping.
"""
    d = dimension(len(matrix))
    if any(len(row) != d for row in matrix):
        raise ValueError('square matrix required')
    for i in range(d):
        for j in range(i):
            if not (matrix[i][j] is matrix[j][i] or matrix[i][j] == matrix[j][i]):
                raise ValueError('symmetric entries must have identical meaning')
    zero = matrix[0][0] * 0
    one = zero + 1
    L = [[one if i == j else zero for j in range(d)] for i in range(d)]
    pivots = []
    for i in range(d):
        pivot = matrix[i][i] - sum((L[i][k] ** 2 * pivots[k] for k in range(i)), zero)
        if not pivot > 0:
            raise ArithmeticError(f'prefix pivot {i+1} is not strictly positive')
        pivots.append(pivot)
        for j in range(i+1, d):
            L[j][i] = (matrix[j][i] - sum((L[j][k] * L[i][k] * pivots[k]
                                         for k in range(i)), zero)) / pivot
    B = [[one if i == j else zero for j in range(d)] for i in range(d)]
    for i in range(d):
        for j in range(i):
            B[i][j] = -sum((L[i][k] * B[k][j] for k in range(j, i)), zero)
    return B, pivots


def imag_divided(poly, x, y_squared):
    """Polynomial Im p(x+iy)/y continued to y=0, with ascending coefficients.

Factoring y before evaluating preserves cancellation across monomials and
avoids treating correlated appearances of y as independent intervals.
"""
    dimension(len(poly))
    value = x * 0
    for j in range(1, len(poly)):
        q = x * 0
        for r in range((j-1)//2 + 1):
            q += (-1)**r * comb(j, 2*r+1) * x**(j-2*r-1) * y_squared**r
        value += poly[j] * q
    return value


def multiply_polynomials(a, b):
    """Small exact polynomial product used for explicit prefix annihilators."""
    if not a or not b or len(a)+len(b)-1 > MAX_DIMENSION+1:
        raise ValueError('invalid polynomial size')
    out = [F(0)] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def annihilator(nodes):
    """Produce product(x-node), never claim a finite prefix is full rank beyond its size."""
    dimension(len(nodes))
    out = [F(1)]
    for node in nodes:
        if type(node) not in (int, F) or node <= 0:
            raise ValueError('positive rational nodes required')
        node = F(node)
        if max(node.numerator.bit_length(), node.denominator.bit_length()) > 64:
            raise ValueError('node exceeds exact test budget')
        out = multiply_polynomials(out, [-node, F(1)])
    return out


def evaluate(poly, x):
    """Evaluate an ascending polynomial by Horner's rule."""
    value = x * 0
    for c in reversed(poly):
        value = value*x+c
    return value


def decision(upper: F) -> str:
    """A failed sufficient bound is inconclusive, not a negative-matrix certificate."""
    if type(upper) not in (int, F) or upper < 0:
        raise ValueError('nonnegative exact upper bound required')
    return 'positive_under_documented_analytic_inputs' if upper < 1 else 'inconclusive'


def cell_may_have_negative_loss(count: int) -> bool:
    """For a reflection-closed height cell, counts zero/one have no off-line pair.

Count >=2 is only a possibility, not a claim that an off-line root exists.
The caller must obtain a complete count including multiplicities.
"""
    if type(count) is not int or not 0 <= count <= 1000000:
        raise ValueError('bounded exact nonnegative full-cell count required')
    return count >= 2
