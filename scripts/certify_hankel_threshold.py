#!/usr/bin/env python3
"""Locate the exact first indefinite block of the HHT006 synthetic spectrum.

All moments include the infinite square spectrum via Euler's even-zeta formula.
A fixed dyadic witness is checked separately from interval LDL. No floating
point, zero tables, network, or canonical Result admission is used.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb, factorial
import json

from certify_localization_blindspot import Interval, pi_interval
from hankel_localization import integer, square_spectrum, power, evaluate, mul

MAX_DIMENSION = 16
WITNESS_DENOMINATOR = 1 << 32
WITNESS_NUMERATORS = (
    -115518064419,
    1632340494941434,
    -3621382919231089108,
    3018566222527092848355,
    -1255147778042128385772473,
    298599267562423032869890910,
    -43823125865723676774859636656,
    4137094325838460656950921650884,
    -256233543422485891476615240302010,
    10435681447990692343922581175639689,
    -275518996099518631221137445246012352,
    4561212314610171752811518858513449213,
    -44613021840893905346978835154409868727,
    232538887396030503027401258830628397727,
    -532504109336058829579307691400574283923,
    340282366920938463463374607431768211456,
)


def bernoulli_extended(n: int) -> list[F]:
    """Compute only the bounded range needed for dimensions at most sixteen."""
    integer(n, 0, 62)
    out = [F(1)]
    for m in range(1, n + 1):
        out.append(-sum((comb(m + 1, k) * out[k] for k in range(m)), F(0)) / (m + 1))
    return out


def complete_moments(d: int = 16, bits: int = 512) -> tuple[list[Interval], list[Interval]]:
    """Enclose the full moments and separately the positive square-spectrum part."""
    integer(d, 1, MAX_DIMENSION)
    integer(bits, 128, 1024)
    pi = pi_interval(bits)
    bern = bernoulli_extended(4 * d - 2)
    target = square_spectrum(F(17, 2), F(1, 4)).target
    positive, moments = [], []
    for j in range(1, 2 * d):
        zeta = (2 * pi).pow(2 * j) * (abs(bern[2 * j]) / (2 * factorial(2 * j)))
        positive.append(zeta)
        moments.append(zeta + 2 * power(target, j)[0])
    return moments, positive


def first_negative_pivot(matrix: list[list[Interval]]) -> tuple[list[Interval], int | None]:
    """A negative upper endpoint certifies a sign; zero-containing intervals do not.

Returns the 1-based first negative Schur pivot after strictly positive ones.
This is a bounded symmetric-matrix routine, not a heuristic eigenvalue test.
"""
    d = integer(len(matrix), 1, MAX_DIMENSION)
    if any(len(row) != d for row in matrix):
        raise ValueError('nonsquare matrix')
    if any(not isinstance(x, Interval) for row in matrix for x in row):
        raise ValueError('interval entries required')
    bits = matrix[0][0].bits
    if any(x.bits != bits for row in matrix for x in row):
        raise ValueError('mixed precision')
    if any(matrix[i][j] != matrix[j][i] for i in range(d) for j in range(d)):
        raise ValueError('nonsymmetric interval matrix')
    a = [row[:] for row in matrix]
    pivots = []
    for k in range(d):
        pivot = a[k][k]
        pivots.append(pivot)
        if pivot.hi < 0:
            return pivots, k + 1
        if pivot.lo <= 0:
            raise ArithmeticError('INCONCLUSIVE: Schur pivot contains zero')
        for i in range(k + 1, d):
            for j in range(i, d):
                updated = a[i][j] - a[i][k] * a[k][j] / pivot
                a[i][j] = updated
                a[j][i] = updated
    return pivots, None


def witness() -> tuple[F, ...]:
    """This proposal is untrusted until its full quadratic interval is negative."""
    return tuple(F(n, WITNESS_DENOMINATOR) for n in WITNESS_NUMERATORS)


def validate_coefficients(coefficients: tuple[F, ...]) -> None:
    """Keep finite-direction calculations exact and within resource bounds."""
    if not isinstance(coefficients, tuple) or not 1 <= len(coefficients) <= MAX_DIMENSION:
        raise ValueError('invalid witness dimension')
    for x in coefficients:
        if isinstance(x, bool) or not isinstance(x, (int, F)):
            raise ValueError('exact witness coefficients required')
        x = F(x)
        if max(x.numerator.bit_length(), x.denominator.bit_length()) > 512:
            raise ValueError('coefficient bit budget')
    if not any(coefficients):
        raise ValueError('zero direction is not a witness')


def quadratic_interval(moments: list[Interval], coefficients: tuple[F, ...]) -> Interval:
    """Directly evaluate the finite quadratic form of the complete moments."""
    validate_coefficients(coefficients)
    d = len(coefficients)
    if len(moments) != 2 * d - 1 or any(not isinstance(x, Interval) for x in moments):
        raise ValueError('wrong moment count or type')
    result = Interval(0, 0, moments[0].bits)
    for i, ci in enumerate(coefficients):
        for j, cj in enumerate(coefficients):
            result = result + moments[i + j] * (ci * cj)
    return result


def spectral_interval(positive: list[Interval], coefficients: tuple[F, ...]) -> Interval:
    """Independent arithmetic layout: square p, sum real spectrum, add exact pair."""
    validate_coefficients(coefficients)
    d = len(coefficients)
    if len(positive) != 2 * d - 1:
        raise ValueError('wrong moment count')
    square = [F(0)] * (2 * d - 1)
    for i, ci in enumerate(coefficients):
        for j, cj in enumerate(coefficients):
            square[i + j] += ci * cj
    target = square_spectrum(F(17, 2), F(1, 4)).target
    value = evaluate(coefficients, target)
    pair = 2 * mul(target, mul(value, value))[0]
    result = Interval(pair, pair, positive[0].bits)
    for c, zeta in zip(square, positive):
        result = result + zeta * c
    return result


def certify(bits: int = 512) -> dict:
    """Require both the first-failure proof and a separately evaluated witness."""
    moments, positive = complete_moments(16, bits)
    matrix = [[moments[i + j] for j in range(16)] for i in range(16)]
    pivots, first = first_negative_pivot(matrix)
    if first != 16:
        raise ArithmeticError('expected first negative pivot not certified')
    p = witness()
    direct = quadratic_interval(moments, p)
    spectral = spectral_interval(positive, p)
    if max(direct.lo, spectral.lo) > min(direct.hi, spectral.hi):
        raise ArithmeticError('the two arithmetic layouts disagree')
    for result in (direct, spectral):
        if not F(-295) < result.lo <= result.hi < F(-294):
            raise ArithmeticError('fixed witness margin not certified')
    return {'bits': bits, 'first_indefinite_dimension': first,
            'pivots': pivots, 'moments': moments,
            'direct_q': direct, 'spectral_q': spectral,
            'witness_numerators': WITNESS_NUMERATORS,
            'witness_denominator': WITNESS_DENOMINATOR,
            'scope': 'synthetic square spectrum, NOT actual xi',
            'kernel_checked_analytic_inputs': False}


def interval_record(x: Interval) -> dict[str, str]:
    """Preserve exact outward endpoints rather than printing only a midpoint."""
    return {'lower': str(x.lo), 'upper': str(x.hi)}


def main() -> int:
    """Two precision runs are a sanity check, not independent software proofs."""
    runs = [certify(bits) for bits in (512, 768)]
    for a, b in zip(runs[0]['moments'], runs[1]['moments']):
        if max(a.lo, b.lo) > min(a.hi, b.hi):
            raise ArithmeticError('cross-precision moment mismatch')
    output = {'schema': 'hht-localization-threshold-v1',
              'scope': runs[0]['scope'], 'canonical_admission': False,
              'witness_numerators': [str(n) for n in WITNESS_NUMERATORS],
              'witness_denominator': str(WITNESS_DENOMINATOR),
              'runs': [{'bits': r['bits'], 'first_indefinite_dimension': 16,
                        'pivots': [interval_record(x) for x in r['pivots']],
                        'direct_q': interval_record(r['direct_q']),
                        'spectral_q': interval_record(r['spectral_q'])} for r in runs]}
    print(json.dumps(output, indent=2))
    print('HHT_THRESHOLD_PASS: full H1..H15 positive; full H16 indefinite; -295<Q(p)<-294; synthetic only.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
