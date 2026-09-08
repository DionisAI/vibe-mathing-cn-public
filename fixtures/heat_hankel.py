#!/usr/bin/env python3
"""Bounded exact arithmetic for a synthetic heat/Hankel counterexample family.

This module checks finite rational identities, not an infinite theorem or RH.
No network, subprocesses, model calls, ledger writes, or third-party packages.
"""
from __future__ import annotations

from fractions import Fraction
from math import factorial

MAX_ORDER = 64
MAX_PARAMETER_BITS = 32
MAX_DIMENSION = 8
Rational = int | Fraction


def parameters(a: Rational, b: Rational, c: Rational) -> tuple[Fraction, Fraction, Fraction]:
    values = []
    for value in (a, b, c):
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
            raise ValueError("parameters must be exact int/Fraction values")
        value = Fraction(value)
        if value <= 0:
            raise ValueError("a, b, c must be positive")
        if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_PARAMETER_BITS:
            raise ValueError("parameter exceeds the fixture bit budget")
        values.append(value)
    return tuple(values)


def order(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, int) or not 0 <= n <= MAX_ORDER:
        raise ValueError(f"order must be an integer in [0, {MAX_ORDER}]")
    return n


def moment(a: Rational, b: Rational, c: Rational, n: int) -> Fraction:
    """a^(-n-1) + 2 Re((b-i*c)^(-n-1)), using rational complex pairs."""
    a, b, c = parameters(a, b, c)
    n = order(n)
    denominator = b*b + c*c
    qr, qi = b/denominator, c/denominator
    real, imag = Fraction(1), Fraction(0)
    for _ in range(n + 1):
        real, imag = real*qr - imag*qi, real*qi + imag*qr
    return a**(-n-1) + 2*real


def moments_from_log_derivative(a: Rational, b: Rational, c: Rational, n: int) -> list[Fraction]:
    """Independent arithmetic route: solve G*(G'/G)=G' coefficient by coefficient."""
    a, b, c = parameters(a, b, c)
    n = order(n)
    denominator = b*b + c*c
    g = [Fraction(1), 1/a + 2*b/denominator,
         1/denominator + 2*b/(a*denominator), 1/(a*denominator)]
    log_coefficients = []
    for degree in range(n + 1):
        value = (degree+1)*g[degree+1] if degree+1 < len(g) else Fraction(0)
        for j in range(1, min(degree, 3) + 1):
            value -= g[j]*log_coefficients[degree-j]
        log_coefficients.append(value)
    return [(-1)**i * value for i, value in enumerate(log_coefficients)]


def hankel(a: Rational, b: Rational, c: Rational, d: int, k: int = 0,
           *, weighted: bool = False) -> list[list[Fraction]]:
    if isinstance(d, bool) or not isinstance(d, int) or not 1 <= d <= MAX_DIMENSION:
        raise ValueError(f"dimension must be in [1, {MAX_DIMENSION}]")
    order(k)
    order(k + 2*(d-1))
    if not isinstance(weighted, bool):
        raise ValueError("weighted must be bool")
    moments = moments_from_log_derivative(a, b, c, k + 2*(d-1))
    return [[moments[k+i+j] * (factorial(k+i+j) if weighted else 1)
             for j in range(d)] for i in range(d)]


def determinant(matrix: list[list[Rational]]) -> Fraction:
    """Exact Gaussian elimination, separate from the closed-form determinant."""
    n = len(matrix)
    if not 1 <= n <= MAX_DIMENSION or any(len(row) != n for row in matrix):
        raise ValueError("expected a nonempty bounded square matrix")
    if any(isinstance(x, bool) or not isinstance(x, (int, Fraction))
           for row in matrix for x in row):
        raise ValueError("matrix entries must be exact rationals")
    rows = [[Fraction(x) for x in row] for row in matrix]
    result = Fraction(1)
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[pivot], rows[column] = rows[column], rows[pivot]
            result = -result
        value = rows[column][column]
        result *= value
        for i in range(column+1, n):
            ratio = rows[i][column]/value
            for j in range(column+1, n):
                rows[i][j] -= ratio*rows[column][j]
            rows[i][column] = Fraction(0)
    return result


def shifted_det_formula(a: Rational, b: Rational, c: Rational, k: int) -> Fraction:
    a, b, c = parameters(a, b, c)
    order(k)
    denominator = b*b + c*c
    separation = (a-b)**2 + c*c
    return -4*c*c*separation**2 / (a**(k+5) * denominator**(k+5))
