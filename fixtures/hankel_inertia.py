#!/usr/bin/env python3
"""Bounded rational finite-spectrum checks. Not a canonical verifier or RH proof.

A spectrum is a list of (real decay, imaginary decay, positive multiplicity).
Conjugate nodes must have equal multiplicity. Repeated entries are aggregated.
Only the Python standard library is used; no network, subprocess or ledger writes.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import factorial

MAX_NODES = 12
MAX_DEGREE = 32
MAX_ORDER = 64
MAX_BITS = 32
MAX_MATRIX_BITS = 16384
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def integer(value, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"expected an integer in [{low}, {high}]")
    return value


def rational(value, bits=MAX_BITS):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError("expected an exact int/Fraction")
    value = F(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > bits:
        raise ValueError("rational exceeds bit budget")
    return value


def add(z, w):
    return z[0] + w[0], z[1] + w[1]


def mul(z, w):
    return z[0]*w[0] - z[1]*w[1], z[0]*w[1] + z[1]*w[0]


def power(z, n):
    integer(n, 0, MAX_ORDER + 1)
    result = ONE
    for _ in range(n):
        result = mul(result, z)
    return result


def reciprocal(z):
    denominator = z[0]**2 + z[1]**2
    if not denominator:
        raise ValueError("zero decay is excluded")
    return z[0]/denominator, -z[1]/denominator


def canonical(spectrum):
    if not isinstance(spectrum, (tuple, list)) or not 1 <= len(spectrum) <= MAX_DEGREE:
        raise ValueError("expected a bounded nonempty spectrum")
    nodes = {}
    for entry in spectrum:
        if not isinstance(entry, (tuple, list)) or len(entry) != 3:
            raise ValueError("expected (real, imag, multiplicity)")
        real, imag, weight = entry
        node = rational(real), rational(imag)
        if node == ZERO:
            raise ValueError("zero decay is excluded")
        weight = integer(weight, 1, MAX_DEGREE)
        nodes[node] = nodes.get(node, 0) + weight
    if len(nodes) > MAX_NODES or sum(nodes.values()) > MAX_DEGREE:
        raise ValueError("spectrum exceeds node/degree budget")
    for (real, imag), weight in nodes.items():
        if nodes.get((real, -imag)) != weight:
            raise ValueError("spectrum must have matching conjugate multiplicities")
    return tuple(sorted(nodes.items()))


def moments(spectrum, n):
    integer(n, 0, MAX_ORDER)
    nodes = canonical(spectrum)
    result = []
    for degree in range(n + 1):
        value = ZERO
        for node, weight in nodes:
            term = power(reciprocal(node), degree + 1)
            value = add(value, (weight*term[0], weight*term[1]))
        if value[1]:
            raise ArithmeticError("real moment has a nonzero imaginary part")
        result.append(value[0])
    return result


def moments_from_polynomial(spectrum, n):
    """Different arithmetic route: construct G and divide G' by G at the origin."""
    integer(n, 0, MAX_ORDER)
    coefficients = [ONE]
    for node, weight in canonical(spectrum):
        u = reciprocal(node)
        for _ in range(weight):
            updated = [ZERO for _ in range(len(coefficients) + 1)]
            for j, coefficient in enumerate(coefficients):
                updated[j] = add(updated[j], coefficient)
                updated[j+1] = add(updated[j+1], mul(coefficient, u))
            coefficients = updated
    if any(value[1] for value in coefficients):
        raise ArithmeticError("G must have real coefficients")
    g = [value[0] for value in coefficients]
    quotient = []
    for degree in range(n + 1):
        value = (degree+1)*g[degree+1] if degree+1 < len(g) else F(0)
        value -= sum(g[j]*quotient[degree-j]
                     for j in range(1, min(degree, len(g)-1) + 1))
        quotient.append(value)
    return [(-1)**i * value for i, value in enumerate(quotient)]


def hankel(spectrum, d, k=0, *, weighted=False):
    integer(d, 1, MAX_NODES)
    integer(k, 0, MAX_ORDER)
    integer(k + 2*(d-1), 0, MAX_ORDER)
    if not isinstance(weighted, bool):
        raise ValueError("weighted must be bool")
    values = moments(spectrum, k + 2*(d-1))
    return [[values[k+i+j] * (factorial(k+i+j) if weighted else 1)
             for j in range(d)] for i in range(d)]


def matrix_copy(matrix, *, symmetric=False):
    if not isinstance(matrix, (tuple, list)):
        raise ValueError("expected a matrix")
    integer(len(matrix), 1, MAX_NODES)
    n = len(matrix)
    if any(not isinstance(row, (tuple, list)) or len(row) != n for row in matrix):
        raise ValueError("expected a square matrix")
    rows = [[rational(x, MAX_MATRIX_BITS) for x in row] for row in matrix]
    if symmetric and any(rows[i][j] != rows[j][i] for i in range(n) for j in range(n)):
        raise ValueError("expected a real symmetric matrix")
    return rows


def determinant(matrix):
    rows = matrix_copy(matrix)
    result = F(1)
    for j in range(len(rows)):
        pivot = next((i for i in range(j, len(rows)) if rows[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            rows[pivot], rows[j] = rows[j], rows[pivot]
            result = -result
        value = rows[j][j]
        result *= value
        for i in range(j+1, len(rows)):
            ratio = rows[i][j]/value
            for h in range(j+1, len(rows)):
                rows[i][h] -= ratio*rows[j][h]
            rows[i][j] = F(0)
    return result


def inertia(matrix):
    """Exact symmetric elimination with 1x1/2x2 pivots, including zero diagonals.

Returns (positive, negative, zero). It does not read the spectrum or its roots.
"""
    rows = matrix_copy(matrix, symmetric=True)
    positive = negative = 0
    while rows:
        n = len(rows)
        pivot = next((i for i in range(n) if rows[i][i]), None)
        if pivot is not None:
            indices = [pivot] + [i for i in range(n) if i != pivot]
            rows = [[rows[i][j] for j in indices] for i in indices]
            value = rows[0][0]
            positive += int(value > 0)
            negative += int(value < 0)
            rows = [[rows[i][j] - rows[i][0]*rows[0][j]/value
                     for j in range(1, n)] for i in range(1, n)]
            continue
        pair = next(((i, j) for i in range(n) for j in range(i+1, n)
                     if rows[i][j]), None)
        if pair is None:
            return positive, negative, n
        i, j = pair
        indices = [i, j] + [h for h in range(n) if h not in pair]
        rows = [[rows[i][j] for j in indices] for i in indices]
        value = rows[0][1]
        positive += 1
        negative += 1
        rows = [[rows[i][j] - (rows[i][0]*rows[j][1] + rows[i][1]*rows[j][0])/value
                 for j in range(2, n)] for i in range(2, n)]
    return positive, negative, 0


def predicted_inertia(spectrum, d, k=0):
    """The finite-spectrum theorem, only for d >= the DISTINCT node count."""
    integer(d, 1, MAX_NODES)
    integer(k, 0, MAX_ORDER)
    nodes = canonical(spectrum)
    if d < len(nodes):
        raise ValueError("full-rank formula is not valid below the distinct node count")
    pairs = sum(node[1] > 0 for node, _ in nodes)
    positive = negative = pairs
    for (real, imag), _ in nodes:
        if imag == 0:
            if real > 0 or k % 2 == 1:
                positive += 1
            else:
                negative += 1
    return positive, negative, d-len(nodes)


def hiding_spectrum(d, q, b):
    integer(d, 1, MAX_NODES)
    integer(q, 1, MAX_NODES//2)
    integer(d + 2*q, 1, MAX_NODES)
    integer(b, 1, 1 << 20)
    return ([(i, 0, 1) for i in range(1, d+1)]
            + [(b+j, sign, 1) for j in range(q) for sign in (-1, 1)])


def hiding_bounds(d, q, b):
    """Rational sufficient conditions from the proof, not sampled shift tests."""
    hiding_spectrum(d, q, b)
    base = hankel([(i, 0, 1) for i in range(1, d+1)], d)
    trace = sum(base[i][i] for i in range(d))
    lower = determinant(base)/trace**(d-1)
    error = F(2*q, b) * sum(F(1, b)**(2*i) for i in range(d))
    return {
        "lower_bound": lower,
        "perturbation_bound": error,
        "margin": lower-error,
        "all_shift_positive": b >= d and error < lower,
        "heat_positive": b >= 2*q + 2,
    }
