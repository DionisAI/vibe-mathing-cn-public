#!/usr/bin/env python3
"""Exact coefficient-cone checks, conditional on the stated sequence hypotheses.

This program does not verify an infinite moment sequence, a root table or RH.
The attached proof shows: positive log-convex moments with m[n+1]/m[n] <= R
satisfy Q_k(p) >= m[k+2e]*(c-B)^2 when B <= c. Here e is the lowest
supported exponent, c its coefficient magnitude, and B the R-weighted mass
of coefficients with the opposite sign. B > c means uncovered, not negative.
All arithmetic in this executable is exact rational arithmetic.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import re
import sys
from typing import Sequence

MAX_TERMS = 257
MAX_DEGREE = 512
MAX_SHIFT = 128
MAX_INPUT_BITS = 8192
MAX_WORK_BITS = 32768
MAX_FILE_BYTES = 1_048_576
MAX_OUTPUT_BYTES = 2_097_152
XI_RADIUS = F(1, 196)
Terms = Sequence[tuple[int, int | F]]


def exact(value: int | F) -> F:
    """Accept only bounded exact rational inputs; bool and float are not rationals here."""
    if type(value) not in (int, F):
        raise ValueError('exact int/Fraction required')
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_INPUT_BITS:
        raise ValueError('rational input exceeds bit budget')
    return value


def _bounded(value: F) -> F:
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_WORK_BITS:
        raise ValueError('intermediate rational exceeds work budget')
    return value


def _power(value: F, exponent: int) -> F:
    bits = max(abs(value.numerator).bit_length(), value.denominator.bit_length(), 1)
    if bits * exponent > MAX_WORK_BITS:
        raise ValueError('power exceeds work budget')
    return _bounded(value ** exponent)


def validate_terms(terms: Terms) -> list[tuple[int, F]]:
    """Check increasing exponents; omit zeros only after validating the input layout."""
    if not isinstance(terms, (list, tuple)) or not 1 <= len(terms) <= MAX_TERMS:
        raise ValueError('term count outside execution budget')
    previous = -1
    out: list[tuple[int, F]] = []
    for item in terms:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError('each term must be (exponent, coefficient)')
        exponent, coefficient = item
        if type(exponent) is not int or not 0 <= exponent <= MAX_DEGREE or exponent <= previous:
            raise ValueError('exponents must be strictly increasing nonnegative bounded integers')
        previous = exponent
        coefficient = exact(coefficient)
        if coefficient:
            out.append((exponent, coefficient))
    if not out:
        raise ValueError('zero polynomial excluded from strict positivity')
    return out


def sign_changes(terms: Terms) -> int:
    data = validate_terms(terms)
    return sum((a > 0) != (b > 0) for (_, a), (_, b) in zip(data, data[1:]))


def classify(terms: Terms, radius: int | F = XI_RADIUS) -> dict:
    """Check a sufficient coefficient condition; never infer the sequence hypotheses."""
    data = validate_terms(terms)
    R = exact(radius)
    if R <= 0:
        raise ValueError('positive ratio upper bound required')
    e, first = data[0]
    c = abs(first)
    initial_sign = 1 if first > 0 else -1
    B = F(0)
    for exponent, coefficient in data[1:]:
        if initial_sign * coefficient < 0:
            B = _bounded(B + _bounded(abs(coefficient) * _power(R, exponent-e)))
    gap = _bounded(c-B)
    if gap > 0:
        status = 'conditional_strict_positive'
    elif gap == 0:
        status = 'conditional_nonnegative_boundary'
    else:
        status = 'uncovered'
    margin = _bounded(gap*gap) if gap >= 0 else None
    return {
        'schema': 'hht-coefficient-cone-v1',
        'status': status,
        'radius': str(R),
        'lowest_exponent': e,
        'degree': data[-1][0],
        'nonzero_terms': len(data),
        'coefficient_sign_changes': sign_changes(data),
        'leading_magnitude': str(c),
        'opposite_weighted_mass': str(B),
        'signed_gap': str(gap),
        'lower_multiplier': str(margin) if margin is not None else None,
        'anchor_moment': f'mu_(k+{2*e})' if margin is not None else None,
        'all_nonnegative_shifts_conditional': margin is not None,
        'sequence_hypotheses': [
            'all moments strictly positive',
            'all adjacent moment ratios nondecreasing',
            'all adjacent moment ratios at most radius',
        ],
        'kernel_input_verified_here': False,
        'lean_compiled_this_iteration': False,
        'rh_proved': False,
        'canonical_admission': False,
    }


def alternating_family(n: int, scale: int = 196) -> list[tuple[int, F]]:
    """p_N=1+sum(scale X)^(2j-1)-(1/(2N))*sum(scale X)^(2j), 1<=j<=N."""
    if type(n) is not int or not 1 <= n <= (MAX_TERMS-1)//2:
        raise ValueError('family size outside execution budget')
    if type(scale) is not int or not 1 <= scale <= 1024:
        raise ValueError('positive bounded integer scale required')
    data = [(0, F(1))]
    for j in range(1, n+1):
        data.extend([(2*j-1, F(scale**(2*j-1))), (2*j, -F(scale**(2*j), 2*n))])
    return validate_terms(data)


def _shift(shift: int) -> int:
    if type(shift) is not int or not 0 <= shift <= MAX_SHIFT:
        raise ValueError('shift outside execution budget')
    return shift


def _moments(moments: Sequence[int | F], needed: int) -> list[F]:
    if not isinstance(moments, (list, tuple)) or not needed < len(moments) <= MAX_SHIFT+2*MAX_DEGREE+1:
        raise ValueError('insufficient or excessive finite moment data')
    return [exact(x) for x in moments[:needed+1]]


def quadratic_form(moments: Sequence[int | F], terms: Terms, shift: int = 0) -> F:
    """Finite coefficient double-sum oracle; it does not certify infinite hypotheses."""
    data = validate_terms(terms)
    k = _shift(shift)
    mu = _moments(moments, k+2*data[-1][0])
    total = F(0)
    for i, ci in data:
        for j, cj in data:
            total = _bounded(total + _bounded(ci*cj*mu[k+i+j]))
    return total


def quadratic_convolution(moments: Sequence[int | F], terms: Terms, shift: int = 0) -> F:
    """Second finite arithmetic route: square the polynomial, then apply the moment map."""
    data = validate_terms(terms)
    k = _shift(shift)
    mu = _moments(moments, k+2*data[-1][0])
    square: dict[int, F] = {}
    for i, ci in data:
        for j, cj in data:
            square[i+j] = _bounded(square.get(i+j, F(0)) + ci*cj)
    total = F(0)
    for power, coefficient in square.items():
        total = _bounded(total + coefficient*mu[k+power])
    return total


def spectral_form(nodes: Sequence[int | F], weights: Sequence[int | F], terms: Terms,
                  shift: int = 0) -> F:
    """Independent finite signed-atomic evaluation; signed weights are intentional tests."""
    if not isinstance(nodes, (list, tuple)) or not isinstance(weights, (list, tuple)):
        raise ValueError('finite lists required')
    if not 1 <= len(nodes) == len(weights) <= 32:
        raise ValueError('invalid finite atomic data')
    data, k = validate_terms(terms), _shift(shift)
    total = F(0)
    for node, weight in zip(nodes, weights):
        u, w = exact(node), exact(weight)
        value = F(0)
        for exponent, coefficient in data:
            value = _bounded(value + coefficient*_power(u, exponent))
        total = _bounded(total + w*_power(u, k+1)*value*value)
    return total


def boundary_moment(n: int) -> F:
    """A positive log-convex bounded sequence whose third-order form is indefinite."""
    if type(n) is not int or not 0 <= n <= MAX_SHIFT+2*MAX_DEGREE:
        raise ValueError('moment index outside execution budget')
    return 1 + F(1, 2**(n+1)) - F(1, 2*4**(n+1))


def boundary_minor_formula(k: int) -> F:
    k = _shift(k)
    return F(1, 4*2**(k+1)) - F(9, 32*4**(k+1)) - F(1, 32*8**(k+1))


def read_polynomial(path: Path) -> list[tuple[int, F]]:
    """Read a bounded JSON list of [integer exponent, exact rational string/integer]."""
    with path.open('rb') as stream:
        raw = stream.read(MAX_FILE_BYTES+1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError('input file exceeds byte budget')
    value = json.loads(raw)
    if not isinstance(value, list) or len(value) > MAX_TERMS:
        raise ValueError('expected bounded list of terms')
    converted = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError('expected [exponent, exact coefficient]')
        exponent, coefficient = pair
        if isinstance(coefficient, str):
            if len(coefficient) > 5000 or not re.fullmatch(r'-?\d+(?:/[1-9]\d*)?', coefficient):
                raise ValueError('coefficient must be an exact integer or fraction string')
            coefficient = F(coefficient)
        converted.append((exponent, coefficient))
    return validate_terms(converted)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--family', type=int, default=None)
    group.add_argument('--polynomial', type=Path)
    args = parser.parse_args()
    terms = read_polynomial(args.polynomial) if args.polynomial else alternating_family(25 if args.family is None else args.family)
    report = classify(terms, XI_RADIUS)
    report['frozen_xi_pr'] = 11
    report['frozen_xi_commit'] = '0d348524e4ea126e37105a51a7adf2fcd2ea17cc'
    text = json.dumps(report, sort_keys=True, indent=2)
    if len(text.encode()) > MAX_OUTPUT_BYTES:
        raise ValueError('output exceeds byte budget')
    print(text)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, OverflowError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
