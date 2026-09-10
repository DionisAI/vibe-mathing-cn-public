#!/usr/bin/env python3
"""Bounded exact minors and a dimension-lifting identity; no zero or RH oracle.

Finite tests of these routines are not a proof of Fekete's theorem. Strict
positivity is never inferred from a zero or an uncertain numerical interval.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from typing import Sequence

MAX_SIZE = 16
MAX_INDEX = 512
MAX_BITS = 4096


def rational(x) -> F:
    """Accept only bounded exact rationals, excluding booleans and floats."""
    if type(x) not in (int, F):
        raise ValueError('exact int/Fraction required')
    x = F(x)
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ValueError('rational bit budget exceeded')
    return x


def indices(values: Sequence[int]) -> tuple[int, ...]:
    """Preserve the increasing index convention needed for minor signs."""
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= MAX_SIZE:
        raise ValueError('nonempty bounded index list required')
    if any(type(x) is not int or not 0 <= x <= MAX_INDEX for x in values):
        raise ValueError('bounded nonnegative integer indices required')
    if any(a >= b for a, b in zip(values, values[1:])):
        raise ValueError('indices must be strictly increasing')
    return tuple(values)


def selected(mu: Sequence, rows: Sequence[int], cols: Sequence[int], k: int = 0) -> list[list]:
    """Select a square Hankel minor; entries can be exact numbers or rigorous balls."""
    rows, cols = indices(rows), indices(cols)
    if type(k) is not int or not 0 <= k <= MAX_INDEX or len(rows) != len(cols):
        raise ValueError('invalid shift or nonsquare minor')
    if k + rows[-1] + cols[-1] >= len(mu):
        raise ValueError('insufficient moments')
    return [[mu[k+i+j] for j in cols] for i in rows]


def determinant(matrix: Sequence[Sequence]) -> F:
    """Exact Gaussian determinant with row swaps, including det(empty)=1."""
    n = len(matrix)
    if n > MAX_SIZE or any(len(row) != n for row in matrix):
        raise ValueError('bounded square matrix required')
    a = [[rational(x) for x in row] for row in matrix]
    det = F(1)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        if p is None:
            return F(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            det = -det
        v = a[j][j]
        det *= v
        for i in range(j+1, n):
            t = a[i][j]/v
            for h in range(j+1, n):
                a[i][h] -= t*a[j][h]
            a[i][j] = F(0)
    return det


def leading_positive_pivots(matrix: Sequence[Sequence]) -> list:
    """No-pivot LU for exact numbers or balls, including nonsymmetric minors.

A positive pivot list certifies positive leading determinants. It certifies
positive definiteness only when the underlying matrix is real symmetric.
"""
    n = len(matrix)
    if not 1 <= n <= MAX_SIZE or any(len(row) != n for row in matrix):
        raise ValueError('nonempty bounded square matrix required')
    if all(type(x) in (int, F) for row in matrix for x in row):
        a = [[rational(x) for x in row] for row in matrix]
    else:
        try:
            from flint import arb
        except ImportError as exc:
            raise ValueError('only exact rationals or FLINT arb entries accepted') from exc
        if any(not isinstance(x, arb) for row in matrix for x in row):
            raise ValueError('mixed or approximate arithmetic is not a certificate')
        if any(not x.is_finite() for row in matrix for x in row):
            raise ArithmeticError('non-finite ball input')
        a = [list(row) for row in matrix]
    pivots = []
    for j in range(n):
        p = a[j][j]
        if not p > 0:
            raise ArithmeticError(f'nonpositive or indeterminate pivot {j+1}')
        pivots.append(p)
        for i in range(j+1, n):
            for h in range(j+1, n):
                a[i][h] -= a[i][j]*a[j][h]/p
    return pivots


def tau(mu: Sequence, d: int, k: int = 0) -> F:
    """Contiguous shifted Hankel determinant, with the empty-minor convention."""
    if type(d) is not int or not 0 <= d <= MAX_SIZE:
        raise ValueError('invalid order')
    if type(k) is not int or not 0 <= k <= MAX_INDEX:
        raise ValueError('invalid shift')
    return F(1) if d == 0 else determinant(selected(mu, tuple(range(d)), tuple(range(d)), k))


def condensation_record(mu: Sequence, d: int, k: int = 0) -> dict[str, F]:
    """Check Desnanot-Jacobi directly by five independently computed determinants."""
    if type(d) is not int or not 1 <= d < MAX_SIZE:
        raise ValueError('condensation order must be between 1 and 15')
    a, b, c = (tau(mu, d, k+j) for j in range(3))
    lower, higher = tau(mu, d-1, k+2), tau(mu, d+1, k)
    defect = a*c - b*b
    if higher*lower != defect:
        raise ArithmeticError('condensation identity mismatch')
    return {'left': a, 'middle': b, 'right': c, 'lower': lower,
            'higher': higher, 'defect': defect}


def next_dimension(a, b, c, lower) -> F:
    """Use the condensation quotient only with a strictly positive denominator."""
    a, b, c, lower = (rational(x) for x in (a, b, c, lower))
    if lower <= 0:
        raise ValueError('strict positive lower-order minor required')
    return (a*c-b*b)/lower


def sparse_quadratic(mu: Sequence, exponents: Sequence[int], coefficients: Sequence,
                     k: int = 0) -> F:
    """Evaluate a real sparse polynomial direction without zero-spectrum truncation."""
    exponents = indices(exponents)
    if len(exponents) != len(coefficients):
        raise ValueError('support and coefficient lengths differ')
    cs = [rational(x) for x in coefficients]
    a = selected(mu, exponents, exponents, k)
    return sum((cs[i]*cs[j]*rational(a[i][j])
                for i in range(len(cs)) for j in range(len(cs))), F(0))


def all_small_minors(matrix: Sequence[Sequence], r: int) -> list[F]:
    """A bounded regression oracle, not an infinite-matrix certification algorithm."""
    n = len(matrix)
    if not 1 <= n <= 6 or any(len(row) != n for row in matrix):
        raise ValueError('regression matrix must be square, size <=6')
    if type(r) is not int or not 1 <= r <= min(n, 4):
        raise ValueError('regression minor order out of budget')
    return [determinant([[matrix[i][j] for j in J] for i in I])
            for s in range(1, r+1) for I in combinations(range(n), s)
            for J in combinations(range(n), s)]
