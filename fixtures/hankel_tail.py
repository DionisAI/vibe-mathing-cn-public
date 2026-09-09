#!/usr/bin/env python3
"""Exact conditional tail bounds; count-envelope truth is an external premise.

No network, subprocess, approximate roots, trusted receipts, or ledger writes.
See HANKEL_TAIL.md for proofs, full-spectrum assumptions and non-claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

MAX_BITS = 256
MAX_CERTIFICATE_BITS = 16384
MAX_DEGREE = 16
MAX_SHIFT = 32
MAX_NODES = 128
MAX_POWER = MAX_SHIFT + 2 * MAX_DEGREE + 1
Rational = int | F
Pair = tuple[F, F]


def rational(value: Rational, *, max_bits: int = MAX_BITS) -> F:
    """Reject floats, booleans and inputs outside a bounded exact-rational domain."""
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError("expected int/Fraction, not a float or bool")
    value = F(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > max_bits:
        raise ValueError("rational input exceeds bit budget")
    return value


def integer(value: int, low: int, high: int) -> int:
    """Validate a bounded integer without silently accepting bool."""
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"expected an integer in [{low}, {high}]")
    return value


def coefficients(values: list[Rational] | tuple[Rational, ...]) -> tuple[F, ...]:
    """Validate a nonzero real polynomial, with coefficients in ascending order."""
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= MAX_DEGREE + 1:
        raise ValueError("polynomial exceeds degree budget or is empty")
    result = tuple(rational(value) for value in values)
    if not any(result):
        raise ValueError("zero polynomial is not a sign witness")
    return result


@dataclass(frozen=True)
class CountEnvelope:
    """Premise: A_R(t) <= (t/R)^alpha*(A+B*log(t/R))+D for all t>=R.

A_R counts only nodes strictly beyond R, including multiplicity. Structural
validation below does not prove the count bound for any supplied spectrum.
"""
    R: Rational
    A: Rational
    alpha: Rational
    B: Rational = 0
    D: Rational = 0

    def __post_init__(self) -> None:
        """Require an increasing, nonnegative envelope on the claimed domain."""
        for name in ("R", "A", "alpha", "B", "D"):
            object.__setattr__(self, name, rational(getattr(self, name)))
        if self.R <= 0 or min(self.A, self.alpha, self.B) < 0 or self.A + self.D < 0:
            raise ValueError("invalid nonnegative count envelope")

    def inverse_power(self, s: int) -> F:
        """Bound sum_{|lambda|>R} m*|lambda|^-s, conditionally on the envelope."""
        s = integer(s, 1, MAX_POWER)
        if s <= self.alpha:
            raise ValueError("s > alpha is required; borderline convergence is not certified")
        gap = F(s) - self.alpha
        return (self.A * s / gap + self.B * s / gap**2 + self.D) / self.R**s


def quadratic_tail_bound(p: list[Rational] | tuple[Rational, ...], k: int,
                         envelope: CountEnvelope) -> F:
    """Bound a fixed p's quadratic tail; zero low terms can improve convergence.

This can be finite even when the entire H_{d,k} is undefined. The caller must
separately require k+1>alpha before making a whole-Hankel-matrix assertion.
"""
    p = coefficients(p)
    k = integer(k, 0, MAX_SHIFT)
    if not isinstance(envelope, CountEnvelope):
        raise ValueError("expected CountEnvelope")
    return sum((abs(ci * cj) * envelope.inverse_power(k + i + j + 1)
                for i, ci in enumerate(p) if ci
                for j, cj in enumerate(p) if cj), F(0))


def matrix_tail_bound(d: int, k: int, envelope: CountEnvelope) -> F:
    """Conditional operator-norm bound for a fixed real symmetric Hankel block."""
    d = integer(d, 1, MAX_DEGREE + 1)
    k = integer(k, 0, MAX_SHIFT)
    if not isinstance(envelope, CountEnvelope):
        raise ValueError("expected CountEnvelope")
    return sum((envelope.inverse_power(k + 2 * j + 1) for j in range(d)), F(0))


def sign_certificate(prefix: Rational, prefix_error: Rational,
                     tail_bound: Rational) -> dict[str, F | str]:
    """Enclose a real quadratic form; equality never certifies a strict sign.

The caller must justify prefix completeness, prefix_error, absolute
convergence, conjugacy, and the tail estimate. This is not a Result receipt.
"""
    prefix, error, tail = (rational(x, max_bits=MAX_CERTIFICATE_BITS)
                           for x in (prefix, prefix_error, tail_bound))
    if error < 0 or tail < 0:
        raise ValueError("error bounds must be nonnegative")
    lower, upper = prefix - error - tail, prefix + error + tail
    decision = ("negative_under_stated_bounds" if upper < 0 else
                "positive_under_stated_bounds" if lower > 0 else "inconclusive")
    return {"lower": lower, "upper": upper, "decision": decision}


def _mul(x: Pair, y: Pair) -> Pair:
    """Multiply rational complex pairs without floating point."""
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def _pow(z: Pair, n: int) -> Pair:
    """Compute a bounded nonnegative integer power by exact repeated squaring."""
    result = (F(1), F(0))
    while n:
        if n & 1:
            result = _mul(result, z)
        z = _mul(z, z)
        n >>= 1
    return result


def _evaluate(p: tuple[F, ...], z: Pair) -> Pair:
    """Evaluate an ascending-order polynomial by Horner's rule."""
    result = (F(0), F(0))
    for c in reversed(p):
        result = _mul(result, z)
        result = result[0] + c, result[1]
    return result


def exact_prefix_quadratic(nodes: list[tuple[Rational, Rational, int]],
                           p: list[Rational] | tuple[Rational, ...], k: int,
                           cutoff: Rational) -> F:
    """Compute sum m*lambda^-k-1*p(1/lambda)^2 for a finite conjugate prefix.

Nodes are (real part, imaginary part, positive integer multiplicity). Checks
ensure every supplied node lies at or below cutoff, not that none is missing.
"""
    p = coefficients(p)
    k = integer(k, 0, MAX_SHIFT)
    cutoff = rational(cutoff)
    if cutoff <= 0 or not isinstance(nodes, (list, tuple)) or not 1 <= len(nodes) <= MAX_NODES:
        raise ValueError("invalid cutoff or node count")
    merged: dict[Pair, int] = {}
    for node in nodes:
        if not isinstance(node, (list, tuple)) or len(node) != 3:
            raise ValueError("expected (real, imag, multiplicity)")
        a, b = rational(node[0]), rational(node[1])
        multiplicity = integer(node[2], 1, 1024)
        norm2 = a * a + b * b
        if not 0 < norm2 <= cutoff * cutoff:
            raise ValueError("node is zero or lies beyond prefix cutoff")
        merged[(a, b)] = merged.get((a, b), 0) + multiplicity
    for (a, b), multiplicity in merged.items():
        if merged.get((a, -b)) != multiplicity:
            raise ValueError("prefix must be conjugate-closed with equal multiplicity")
    result = (F(0), F(0))
    for (a, b), multiplicity in merged.items():
        norm2 = a * a + b * b
        u = (a / norm2, -b / norm2)
        value = _evaluate(p, u)
        term = _mul(_pow(u, k + 1), _mul(value, value))
        result = (result[0] + multiplicity * term[0],
                  result[1] + multiplicity * term[1])
    if result[1]:
        raise ArithmeticError("conjugacy invariant failed")
    return result[0]


def square_tail_envelope(scale: Rational, included: int) -> CountEnvelope:
    """Proved envelope for {scale*n^2 : n>included}, not for arbitrary spectra."""
    scale = rational(scale)
    included = integer(included, 1, MAX_NODES - 3)
    if scale <= 0:
        raise ValueError("scale must be positive")
    return CountEnvelope(scale * included**2, included, F(1, 2), D=-included)


def synthetic_certificate(scale: int = 32, included: int = 1) -> dict[str, F | str]:
    """Evaluate the documented infinite example; all spectral premises are proved.

The result still has a conditional label: code execution is not independent
proof review or admission into the trusted mathematical result ledger.
"""
    scale = integer(scale, 3, 1024)
    included = integer(included, 1, MAX_NODES - 3)
    envelope = square_tail_envelope(scale, included)
    nodes = [(1, 0, 1), (2, 1, 1), (2, -1, 1)]
    nodes.extend((scale * n * n, 0, 1) for n in range(1, included + 1))
    p = (F(2, 5), -F(7, 5), F(1))
    prefix = exact_prefix_quadratic(nodes, p, 0, envelope.R)
    tail = quadratic_tail_bound(p, 0, envelope)
    return {**sign_certificate(prefix, 0, tail), "prefix": prefix,
            "tail_bound": tail, "cutoff": envelope.R}
