#!/usr/bin/env python3
"""Finite exact regressions; not a verification of every actual-xi moment."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import tempfile
import unittest

import hht_coefficient_cone as M


class ConeTests(unittest.TestCase):
    def test_family_twenty_five(self):
        result = M.classify(M.alternating_family(25))
        self.assertEqual(result['nonzero_terms'], 51)
        self.assertEqual(result['degree'], 50)
        self.assertEqual(result['coefficient_sign_changes'], 49)
        self.assertEqual(result['opposite_weighted_mass'], '1/2')
        self.assertEqual(result['lower_multiplier'], '1/4')
        self.assertEqual(result['status'], 'conditional_strict_positive')

    def test_family_grid(self):
        for n in (1, 2, 5, 10, 25, 64, 128):
            result = M.classify(M.alternating_family(n))
            self.assertEqual(result['lower_multiplier'], '1/4')
            self.assertEqual(result['coefficient_sign_changes'], 2*n-1)

    def test_same_sign_magnitudes_unrestricted_within_budget(self):
        p = [(0, F(2)), (1, F(10**100)), (4, -F(1, 4)), (7, F(10**200))]
        result = M.classify(p, 1)
        self.assertEqual(result['opposite_weighted_mass'], '1/4')
        self.assertEqual(result['lower_multiplier'], '49/16')

    def test_no_opposite_coefficients(self):
        result = M.classify([(0, 3), (2, 10), (8, 10**100)])
        self.assertEqual(result['opposite_weighted_mass'], '0')
        self.assertEqual(result['lower_multiplier'], '9')

    def test_zero_coefficients_ignored(self):
        result = M.classify([(0, 0), (2, -1), (3, 0), (4, F(1, 2))], 1)
        self.assertEqual(result['lowest_exponent'], 2)
        self.assertEqual(result['coefficient_sign_changes'], 1)
        self.assertEqual(result['anchor_moment'], 'mu_(k+4)')
        self.assertEqual(result['lower_multiplier'], '1/4')

    def test_global_negation(self):
        p = [(0, F(2)), (2, -F(1, 2)), (4, F(3))]
        self.assertEqual(M.classify(p, 1), M.classify([(e, -c) for e,c in p], 1))

    def test_positive_rescaling(self):
        p = [(0, F(2)), (1, -F(1, 2)), (3, F(7))]
        a = M.classify(p, 1)
        b = M.classify([(e, 3*c) for e,c in p], 1)
        self.assertEqual(F(b['lower_multiplier']), 9*F(a['lower_multiplier']))

    def test_initial_exponent_shift(self):
        p = [(0, F(1)), (2, -F(1, 3)), (5, F(2))]
        shifted = [(e+4, c) for e,c in p]
        a, b = M.classify(p, 1), M.classify(shifted, 1)
        self.assertEqual(a['lower_multiplier'], b['lower_multiplier'])
        self.assertEqual(b['anchor_moment'], 'mu_(k+8)')
        mu = [M.boundary_moment(n) for n in range(24)]
        self.assertEqual(M.quadratic_form(mu, shifted, 2), M.quadratic_form(mu, p, 10))

    def test_boundary_does_not_claim_strictness(self):
        p = [(0, F(1)), (1, -F(2))]
        result = M.classify(p, F(1, 2))
        self.assertEqual(result['status'], 'conditional_nonnegative_boundary')
        self.assertEqual(result['lower_multiplier'], '0')
        self.assertEqual(M.spectral_form([F(1, 2)], [1], p), 0)

    def test_uncovered_not_a_negative_certificate(self):
        result = M.classify([(0, 1), (1, -2)], 1)
        self.assertEqual(result['status'], 'uncovered')
        self.assertIsNone(result['lower_multiplier'])
        self.assertFalse(result['all_nonnegative_shifts_conditional'])
        self.assertGreater(M.spectral_form([1], [1], [(0,1), (1,-2)]), 0)

    def test_indefinite_boundary_example(self):
        p = [(0, F(1,2)), (1, -F(3,2)), (2, F(1))]
        mu = [M.boundary_moment(n) for n in range(5)]
        self.assertEqual(M.quadratic_form(mu, p), -F(9, 2048))
        self.assertEqual(M.spectral_form([1,F(1,2),F(1,4)], [1,1,-F(1,2)], p), -F(9,2048))
        self.assertEqual(M.classify(p, 1)['status'], 'uncovered')
        h = [[mu[i+j] for j in range(3)] for i in range(3)]
        det = (h[0][0]*(h[1][1]*h[2][2]-h[1][2]*h[2][1])
               -h[0][1]*(h[1][0]*h[2][2]-h[1][2]*h[2][0])
               +h[0][2]*(h[1][0]*h[2][1]-h[1][1]*h[2][0]))
        self.assertEqual(det, -F(9,16384))

    def test_global_formula_finite_checks(self):
        # A universal algebraic proof is in the note; 65 shifts are regressions only.
        for k in range(65):
            x, y, z = [M.boundary_moment(k+j) for j in range(3)]
            self.assertGreater(x, 0)
            self.assertLessEqual(x, F(3,2))
            self.assertLess(y, x)
            self.assertEqual(x*z-y*y, M.boundary_minor_formula(k))
            self.assertGreaterEqual(x*z-y*y, F(13, 128*2**(k+1)))

    def test_all_gap_rank_one_lower_bound(self):
        mu = [M.boundary_moment(n) for n in range(24)]
        for k, i, j in product(range(5), range(6), range(6)):
            self.assertGreaterEqual(mu[k]*mu[k+i+j], mu[k+i]*mu[k+j])
            self.assertLessEqual(mu[k+i+j], mu[k+i])

    def test_coefficient_grid_on_indefinite_sequence(self):
        # 5^4 coefficient patterns, three shifts, two arithmetic routes per pattern.
        mu = [M.boundary_moment(n) for n in range(12)]
        choices = (-F(1,2), -F(1,4), F(0), F(1,4), F(1,2))
        for coefficients in product(choices, repeat=4):
            p = [(0,F(2))]+list(enumerate(coefficients, start=1))
            report = M.classify(p, 1)
            self.assertNotEqual(report['status'], 'uncovered')
            for k in range(3):
                q = M.quadratic_form(mu,p,k)
                self.assertEqual(q, M.quadratic_convolution(mu,p,k))
                self.assertGreaterEqual(q, mu[k]*F(report['lower_multiplier']))

    def test_three_atomic_and_coefficient_routes(self):
        mu = [M.boundary_moment(n) for n in range(30)]
        for n in (1,2,5):
            p = M.alternating_family(n, scale=1)
            for k in (0,1,7):
                q = M.spectral_form([1,F(1,2),F(1,4)], [1,1,-F(1,2)], p,k)
                self.assertEqual(q,M.quadratic_form(mu,p,k))
                self.assertEqual(q,M.quadratic_convolution(mu,p,k))
                self.assertGreaterEqual(q,mu[k]/4)

    def test_scaled_radius_family_with_many_changes(self):
        # Not actual xi: a deliberately indefinite rational model obeying the hypotheses.
        R = M.XI_RADIUS
        p = M.alternating_family(25)
        mu = [R**(n+1)*M.boundary_moment(n) for n in range(108)]
        for k in (0,7):
            q = M.quadratic_form(mu,p,k)
            self.assertEqual(q,M.spectral_form([R,R/2,R/4], [1,1,-F(1,2)],p,k))
            self.assertGreaterEqual(q,mu[k]/4)

    def test_no_invented_kernel_or_rh_flags(self):
        report = M.classify([(0,1)])
        for key in ('kernel_input_verified_here','lean_compiled_this_iteration','rh_proved','canonical_admission'):
            self.assertFalse(report[key])
        self.assertEqual(len(report['sequence_hypotheses']),3)

    def test_invalid_coefficients_and_radius(self):
        for bad in (True, 0.25, '1/4', None):
            with self.assertRaises(ValueError):
                M.classify([(0,bad)])
            with self.assertRaises(ValueError):
                M.classify([(0,1)],bad)
        for bad in (0,-1):
            with self.assertRaises(ValueError):
                M.classify([(0,1)],bad)

    def test_invalid_exponents_duplicates_and_shape(self):
        for p in ([], [(0,0)], [(0,1),(0,2)], [(2,1),(1,2)], [(True,1)],
                  [(-1,1)], [(1.5,1)], [(1000000,1)], [(0,1,2)]):
            with self.assertRaises(ValueError):
                M.classify(p)

    def test_bit_and_count_budget(self):
        with self.assertRaises(ValueError):
            M.classify([(0,1 << 8192)])
        with self.assertRaises(ValueError):
            M._power(F(2**1024),40)
        with self.assertRaises(ValueError):
            M.classify([(i,1) for i in range(258)])
        for n in (0,-1,True,129):
            with self.assertRaises(ValueError):
                M.alternating_family(n)

    def test_quadratic_contracts(self):
        for bad in (-1,True,129):
            with self.assertRaises(ValueError):
                M.quadratic_form([1,2,3],[(0,1)],bad)
        with self.assertRaises(ValueError):
            M.quadratic_form([1,2],[(0,1),(1,1)])
        with self.assertRaises(ValueError):
            M.quadratic_form([1.0],[(0,1)])
        with self.assertRaises(ValueError):
            M.spectral_form([1],[1,2],[(0,1)])

    def test_json_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'polynomial.json'
            p.write_text('[[0,"1"],[2,"-1/2"],[5,3]]')
            data = M.read_polynomial(p)
            self.assertEqual(data,[(0,F(1)),(2,-F(1,2)),(5,F(3))])
            for bad in ('[[0,1.0]]','[[0,true]]','[[0,"1e100"]]','[[0,"1/0"]]',
                        '[[0,"1"],[0,"2"]]','{}'):
                p.write_text(bad)
                with self.assertRaises(ValueError):
                    M.read_polynomial(p)


if __name__ == '__main__':
    unittest.main(verbosity=2)
