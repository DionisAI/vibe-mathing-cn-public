#!/usr/bin/env python3
"""Exact threshold/witness tests; compilation is a separate verification step."""
from fractions import Fraction as F
from math import comb
import unittest

from certify_localization_blindspot import Interval as I, bernoulli
from certify_hankel_threshold import (
    bernoulli_extended, complete_moments, first_negative_pivot,
    witness, quadratic_interval, spectral_interval, certify,
)


class ThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Cache two complete runs, not a subset of their matrix entries."""
        cls.runs = [certify(bits) for bits in (512, 768)]

    def test_exact_first_indefinite_dimension(self):
        """All smaller leading blocks are positive, not merely the first eight."""
        for r in self.runs:
            self.assertEqual(r['first_indefinite_dimension'], 16)
            self.assertEqual(len(r['pivots']), 16)
            self.assertTrue(all(x.lo > 0 for x in r['pivots'][:15]))
            self.assertLess(r['pivots'][15].hi, 0)

    def test_fixed_witness_strict_interval(self):
        """Direct and spectrally regrouped evaluations both keep the whole interval negative."""
        for r in self.runs:
            for key in ('direct_q', 'spectral_q'):
                self.assertLess(F(-295), r[key].lo)
                self.assertLess(r[key].hi, F(-294))

    def test_cross_precision(self):
        """Independent precision runs must not produce contradictory enclosures."""
        for a, b in zip(self.runs[0]['moments'], self.runs[1]['moments']):
            self.assertLessEqual(max(a.lo, b.lo), min(a.hi, b.hi))

    def test_polynomial_degree(self):
        """The proposed polynomial has exact degree fifteen with dyadic coefficients."""
        p = witness()
        self.assertEqual(len(p), 16)
        self.assertEqual(p[-1], 2**96)
        self.assertTrue(all((c * 2**32).denominator == 1 for c in p))

    def test_wrong_witness_is_not_accepted_by_sign(self):
        """A positive direction cannot become a negative certificate by supplying the wrong vector."""
        p = (F(1),) + (F(0),) * 15
        q = quadratic_interval(self.runs[0]['moments'], p)
        self.assertGreater(q.lo, 0)

    def test_small_spectral_regroupings(self):
        """Regroup convolution and node evaluation for several exact directions."""
        for d in range(1, 6):
            mu, pos = complete_moments(d, 256)
            p = tuple(F((-1)**j, j+1) for j in range(d))
            a, b = quadratic_interval(mu, p), spectral_interval(pos, p)
            self.assertLessEqual(max(a.lo, b.lo), min(a.hi, b.hi))

    def test_known_positive_schur(self):
        """Exact reference matrix has two positive Schur pivots."""
        p, first = first_negative_pivot([[I(2,2), I(1,1)], [I(1,1), I(2,2)]])
        self.assertIsNone(first)
        self.assertEqual([x.lo for x in p], [2, F(3,2)])

    def test_known_negative_schur(self):
        """Strictly negative upper bounds are distinct from failed positivity."""
        p, first = first_negative_pivot([[I(1,1), I(0,0)], [I(0,0), I(-1,-1)]])
        self.assertEqual(first, 2)
        self.assertEqual(p[-1].hi, -1)

    def test_uncertain_and_zero_pivots_are_inconclusive(self):
        """An interval meeting zero must not be reported as negative."""
        for p in (I(-1,1), I(0,0), I(0,1)):
            with self.assertRaises(ArithmeticError):
                first_negative_pivot([[p]])

    def test_asymmetry_rejected(self):
        """The certificate only applies to one underlying symmetric matrix."""
        with self.assertRaises(ValueError):
            first_negative_pivot([[I(1,1), I(0,0)], [I(1,1), I(1,1)]])

    def test_bad_matrices_rejected(self):
        """Keep dimensions, types, and precision within the documented domain."""
        for m in ([], [[I(1,1), I(0,0)]], [[1]],
                  [[I(1,1,128), I(0,0,256)], [I(0,0,256), I(1,1,128)]],
                  [[I(1,1)]*17 for _ in range(17)]):
            with self.assertRaises(ValueError):
                first_negative_pivot(m)

    def test_bad_coefficients_rejected(self):
        """Reject zero witnesses, floats, booleans, oversized inputs and shape errors."""
        for p in ((), (0,), (True,), (0.5,), (1<<600,), [1]):
            with self.assertRaises(ValueError):
                quadratic_interval([I(1,1)], p)
        with self.assertRaises(ValueError):
            quadratic_interval([I(1,1)], witness())

    def test_bernoulli_extension(self):
        """The extension preserves every old coefficient and its defining recurrence."""
        b = bernoulli_extended(62)
        self.assertEqual(b[:31], bernoulli(30))
        for m in range(1, 63):
            self.assertEqual(sum(F(comb(m+1,k))*b[k] for k in range(m+1)), 0)

    def test_numeric_scope_budgets(self):
        """No arbitrary precision or dimension escalation through caller inputs."""
        for d in (0, 17, True, 1.5):
            with self.assertRaises(ValueError): complete_moments(d)
        for bits in (64, 2048, True):
            with self.assertRaises(ValueError): complete_moments(1, bits)
        with self.assertRaises(ValueError): bernoulli_extended(63)

    def test_rank_one_pair_identity_exact_grid(self):
        """Check the rank-one decomposition used to classify every larger dimension."""
        for x in (F(1,3), F(2)):
            for y in (F(-1,4), F(3,7)):
                for P in (F(0), F(2,5)):
                    for Q in (F(0), F(-3,8)):
                        lhs = 2*(x*(P*P-Q*Q)-2*y*P*Q)
                        rhs = 2*x*(P-y*Q/x)**2 - 2*(x*x+y*y)*Q*Q/x
                        self.assertEqual(lhs, rhs)

    def test_scope_is_not_xi_or_lean(self):
        """Numerical evidence never promotes itself to a different function or proof system."""
        for r in self.runs:
            self.assertIn('NOT actual xi', r['scope'])
            self.assertFalse(r['kernel_checked_analytic_inputs'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
