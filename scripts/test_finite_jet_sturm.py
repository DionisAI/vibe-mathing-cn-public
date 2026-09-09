#!/usr/bin/env python3
"""Separate exact Sturm-chain check of finite-jet twin real-root counts.

This does not use the disk certificate to decide the real-root counts. Sturm's
classical sign-variation theorem remains an explicit mathematical input;
this Python implementation is not a Lean-certified Sturm algorithm.
"""
from fractions import Fraction as F
from math import gcd, lcm
import unittest
from certify_finite_jet_twins import construct


def _trim(p):
    """Delete leading zeros without changing the represented polynomial."""
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def _primitive(p):
    """Use positive scaling only, so every Sturm-chain sign is preserved."""
    p = _trim(p)
    if not p:
        return []
    if any(max(x.numerator.bit_length(), x.denominator.bit_length()) > 200000 for x in p):
        raise ArithmeticError('intermediate rational budget exceeded')
    denominator = lcm(*(x.denominator for x in p))
    integers = [int(x*denominator) for x in p]
    common = gcd(*integers)
    return [F(x//common) for x in integers]


def _remainder(a, b):
    """Exact Euclidean remainder, whose degree strictly decreases in each step."""
    a = list(a)
    while len(a) >= len(b):
        shift = len(a)-len(b)
        factor = a[-1]/b[-1]
        for j in range(len(b)):
            a[shift+j] -= factor*b[j]
        a = _trim(a)
    return a


def _sign(x):
    """The sign of an exact rational, with no tolerance threshold."""
    return int(x > 0)-int(x < 0)


def _variations(signs):
    """Sturm convention: discard zeros when counting adjacent sign changes."""
    signs = [x for x in signs if x]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def real_root_counts(p):
    """Count real and positive real roots of a squarefree polynomial, not approximate them."""
    if not isinstance(p, tuple) or not 2 <= len(p) <= 33:
        raise ValueError('expected degree between 1 and 32')
    if any(isinstance(x, bool) or not isinstance(x, (int, F)) for x in p):
        raise ValueError('exact non-boolean rational coefficients required')
    p = tuple(F(x) for x in p)
    if any(max(x.numerator.bit_length(), x.denominator.bit_length()) > 16384 for x in p):
        raise ValueError('input bit budget exceeded')
    if p[-1] == 0 or p[0] == 0:
        raise ValueError('nonzero leading coefficient and zero-endpoint exclusion required')
    sequence = [_primitive(p), _primitive([k*p[k] for k in range(1, len(p))])]
    while True:
        next_poly = _primitive([-x for x in _remainder(sequence[-2], sequence[-1])])
        if not next_poly:
            break
        if len(next_poly) >= len(sequence[-1]):
            raise ArithmeticError('Sturm degree invariant failed')
        sequence.append(next_poly)
    if len(sequence[-1]) != 1:
        raise ArithmeticError('repeated roots are outside this certificate contract')
    positive_inf = _variations([_sign(q[-1]) for q in sequence])
    negative_inf = _variations([(-1)**(len(q)-1)*_sign(q[-1]) for q in sequence])
    at_zero = _variations([_sign(q[0]) for q in sequence])
    return {'real': negative_inf-positive_inf, 'positive': at_zero-positive_inf,
            'variations': (negative_inf, at_zero, positive_inf),
            'gcd_degree': 0, 'kernel_checked': False}


class SturmTests(unittest.TestCase):
    def test_twins(self):
        """Without consulting disk signs, count all roots over the whole real line."""
        t = construct()
        a, b = real_root_counts(t.p_real), real_root_counts(t.p_nonreal)
        self.assertEqual((a['real'], a['positive']), (16, 16))
        self.assertEqual((b['real'], b['positive']), (14, 14))
        self.assertEqual((a['gcd_degree'], b['gcd_degree']), (0, 0))
        self.assertFalse(a['kernel_checked'])

    def test_known_polynomials(self):
        """Cover positive, negative, irrational and exclusively nonreal roots."""
        for p, expected in (((-2, 0, 1), (2, 1)), ((1, 0, 1), (0, 0)),
                            ((-6, 1, 1), (2, 1)), ((2, -3, 1), (2, 2)),
                            ((1, 0, 0, 0, 1), (0, 0)), ((2, 1), (1, 0))):
            r = real_root_counts(p)
            self.assertEqual((r['real'], r['positive']), expected)

    def test_scale_invariance(self):
        """Negative leading coefficients must not flip the Sturm root counts."""
        for scalar in (F(3, 7), -F(17, 5), F(1000)):
            r = real_root_counts(tuple(scalar*x for x in (2, -3, 1)))
            self.assertEqual((r['real'], r['positive']), (2, 2))

    def test_rejections(self):
        """Reject repeated roots, an endpoint root, floats, bools and resource overflow."""
        with self.assertRaises(ArithmeticError):
            real_root_counts((1, -2, 1))
        for p in ((0, -1, 1), (1, 0), (0.5, 1), (True, 1), (1,), [],
                  (1 << 17000, 1), tuple(range(34))):
            with self.assertRaises(ValueError):
                real_root_counts(p)


if __name__ == '__main__':
    unittest.main(verbosity=2)
