#!/usr/bin/env python3
"""Exact rectangular coefficient bounds; infinite-sequence premises stay explicit."""
from __future__ import annotations
from fractions import Fraction as F
from hht_coefficient_cone import (XI_RADIUS, Terms, exact, _bounded, _power,
                                 validate_terms, sign_changes, MAX_TERMS)

XI_LOWER_RATIO = F(1, 625)


def distance_squared(center: F, low: F, high: F) -> F:
    """Squared distance from a rational center to a closed rational interval."""
    center, low, high = exact(center), exact(low), exact(high)
    if low > high:
        raise ValueError('interval endpoints reversed')
    delta = low-center if center < low else center-high if high < center else F(0)
    return _bounded(delta*delta)


def rectangle_bound(c: F, ua: F, ub: F, va: F, vb: F) -> F:
    """Minimum of (c-v)^2+u^2+2(c-vb)u on the specified rectangle."""
    c, ua, ub, va, vb = map(exact, (c, ua, ub, va, vb))
    if c <= 0 or not 0 <= ua <= ub or not 0 <= va <= vb:
        raise ValueError('invalid positive constant or nonnegative rectangle')
    return _bounded(distance_squared(c, va, vb)
                    +distance_squared(vb-c, ua, ub)-(vb-c)**2)


def classify_balance(terms: Terms, lower: int | F = XI_LOWER_RATIO,
                     upper: int | F = XI_RADIUS) -> dict:
    """Certify a bound conditionally; a negative bound is NOT a negative form."""
    data = validate_terms(terms)
    low, high = exact(lower), exact(upper)
    if not 0 < low <= high:
        raise ValueError('require 0 < lower ratio <= upper ratio')
    e, first = data[0]
    c, sign = abs(first), 1 if first > 0 else -1
    al = ar = bl = br = F(0)
    for exponent, coefficient in data[1:]:
        power = exponent-e
        x = _bounded(abs(coefficient)*_power(low, power))
        y = _bounded(abs(coefficient)*_power(high, power))
        if sign*coefficient > 0:
            al, ar = _bounded(al+x), _bounded(ar+y)
        else:
            bl, br = _bounded(bl+x), _bounded(br+y)
    bound = rectangle_bound(c, al, ar, bl, br)
    status = ('conditional_strict_positive' if bound > 0 else
              'conditional_nonnegative' if bound == 0 else 'inconclusive')
    return {
        'schema': 'hht-balance-v1', 'status': status,
        'constant_magnitude': str(c), 'lowest_exponent': e,
        'positive_mass_interval': [str(al), str(ar)],
        'opposite_mass_interval': [str(bl), str(br)],
        'ratio_interval': [str(low), str(high)],
        'lower_multiplier': str(bound), 'anchor': f'mu_(k+{2*e})',
        'nonzero_terms': len(data), 'sign_changes': sign_changes(data),
        'old_amplitude_condition_holds': br <= c,
        'all_shifts_conditional': True,
        'premises': ['positive moments', 'nondecreasing adjacent ratios',
                     'all adjacent ratios in stated interval'],
        'sequence_premises_verified_here': False,
        'negative_bound_is_counterexample': False,
        'rh_proved': False, 'canonical_admission': False,
    }


def rescued_family(n: int, scale: int = 196) -> list[tuple[int, F]]:
    """1+8Y+sum_{j=2}^N Y^(2j-1)-(2/N)sum_{j=1}^N Y^(2j), Y=scale X."""
    if type(n) is not int or not 1 <= n <= (MAX_TERMS-1)//2:
        raise ValueError('family size outside execution budget')
    if type(scale) is not int or not 1 <= scale <= 1024:
        raise ValueError('invalid scale')
    terms = [(0, F(1))]
    for j in range(1, n+1):
        terms += [(2*j-1, F((8 if j == 1 else 1)*scale**(2*j-1))),
                  (2*j, -F(2*scale**(2*j), n))]
    return validate_terms(terms)
