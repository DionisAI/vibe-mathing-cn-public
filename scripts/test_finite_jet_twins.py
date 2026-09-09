#!/usr/bin/env python3
"""Exact regression and tamper tests; analytic root counts use stated theorems."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest
import certify_finite_jet_twins as T


class FiniteJetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Generate one frozen exact certificate reused by adversarial tests."""
        cls.t = T.construct()

    def test_default_exact_matching(self):
        """Fifteen power sums and the entire eight-dimensional block coincide."""
        t = self.t
        a, b = T.power_sums(t.p_real, 16), T.power_sums(t.p_nonreal, 16)
        self.assertEqual(a[:15], b[:15])
        self.assertEqual([[a[i+j] for j in range(8)] for i in range(8)],
                         [[b[i+j] for j in range(8)] for i in range(8)])
        self.assertNotEqual(a[15], b[15])
        self.assertEqual(b[15]-a[15], -32*t.epsilon)

    def test_parameter_grid(self):
        """Different finite jet lengths and low-root prefixes meet all premises."""
        for d, H in product((2, 3, 4, 8), (1, 7, 50, 100)):
            with self.subTest(d=d, H=H):
                r = T.verify(T.construct(d, H))
                self.assertEqual(r['matching_moments'], 2*d-1)
                self.assertEqual(r['nonreal_polynomial_conjugate_pairs'], 1)

    def test_resource_boundary_case(self):
        """The maximal supported degree and height still produce finite certificates."""
        r = T.verify(T.construct(16, T.MAX_HEIGHT))
        self.assertEqual((r['degree'], r['unchanged_root_prefix_height']), (32, T.MAX_HEIGHT))

    def test_two_algebraic_routes(self):
        """Newton sums equal separately computed logarithmic-derivative coefficients."""
        for p in (self.t.p_real, self.t.p_nonreal):
            self.assertEqual(T.power_sums(p, 16),
                             T.logarithmic_moments(T.factor_coefficients(p), 16))

    def test_known_power_sum_oracle(self):
        """Newton recurrence agrees with direct rational powers at explicit nodes."""
        roots = (F(1, 2), F(2, 3), F(5, 4), F(7, 5))
        p = (F(1),)
        for u in roots:
            p = T.mul(p, (-u, F(1)))
        self.assertEqual(T.power_sums(p, 4),
                         tuple(sum((u**k for u in roots), F(0)) for k in range(1, 5)))

    def test_jet_and_first_difference(self):
        """Reversed factors agree through degree fifteen, with an exact next term."""
        f, g = map(T.factor_coefficients, (self.t.p_real, self.t.p_nonreal))
        self.assertEqual(f[:-1], g[:-1])
        self.assertEqual(g[-1]-f[-1], 2*self.t.epsilon)
        self.assertEqual((f[0], g[0]), (1, 1))

    def test_strict_boundary_and_target_signs(self):
        """Root-disposition decisions have positive rational separation from zero."""
        t = self.t
        self.assertTrue(all(B >= 4*t.epsilon > t.epsilon for B in t.boundary_bounds))
        r, h = t.centers[-1], t.radius
        self.assertLess(T.evaluate(t.p_real, r), 0)
        for x in (r-h, r+h):
            self.assertGreater(T.evaluate(t.p_real, x), 0)
        self.assertEqual(T.evaluate(t.p_nonreal, r), t.epsilon)

    def test_strip_height_and_heat_margins(self):
        """Exact sufficient inequalities certify the full disks, not sampled roots."""
        t = self.t; r, h, H = t.centers[-1], t.radius, t.prefix_height
        self.assertLess(h*h, (r-h)**3)
        self.assertGreater(r-2*h, (r+h)**2)
        self.assertGreater(r-h, H*H*(r+h)**2)
        self.assertGreater(r-h, F(1, (H+16)**2))

    def test_swapped_signs_rejected(self):
        """A caller cannot swap real/nonreal labels while retaining the certificate."""
        with self.assertRaises(ArithmeticError):
            T.verify(replace(self.t, p_real=self.t.p_nonreal, p_nonreal=self.t.p_real))

    def test_coefficient_tampering_rejected(self):
        """Changing a coefficient cannot retain the root or jet certification."""
        for attr in ('p0', 'p_real', 'p_nonreal'):
            p = list(getattr(self.t, attr)); p[1] += F(1, 10**9)
            with self.subTest(attr=attr), self.assertRaises(ArithmeticError):
                T.verify(replace(self.t, **{attr: tuple(p)}))

    def test_boundary_tampering_rejected(self):
        """The verifier recomputes the full boundary bound instead of trusting it."""
        B = list(self.t.boundary_bounds); B[0] *= 2
        with self.assertRaises(ArithmeticError):
            T.verify(replace(self.t, boundary_bounds=tuple(B)))
        for e in (0, -self.t.epsilon, 2*self.t.epsilon):
            with self.assertRaises(ArithmeticError):
                T.verify(replace(self.t, epsilon=e))

    def test_head_identity_and_shape_rejected(self):
        """A certificate is bound to its precise unchanged/removed square-spectrum block."""
        for kw in ({'centers': ()}, {'ordinates': self.t.ordinates[::-1]},
                   {'prefix_height': 51}, {'centers': self.t.centers[::-1]},
                   {'p_real': self.t.p_real[:-1]}, {'boundary_bounds': ()}):
            with self.subTest(kw=next(iter(kw))), self.assertRaises(ArithmeticError):
                T.verify(replace(self.t, **kw))

    def test_scalar_and_budget_rejections(self):
        """No floats, bools, invalid domains or unbounded certificate integers."""
        for d, H in ((1, 50), (17, 50), (True, 50), (8, 0), (8, T.MAX_HEIGHT+1), (8, 1.5)):
            with self.assertRaises(ValueError):
                T.construct(d, H)
        for attr, val in (('radius', 0.5), ('epsilon', True), ('epsilon', F(1, 1 << 17000)),
                          ('dimension', True), ('p0', list(self.t.p0))):
            with self.subTest(attr=attr), self.assertRaises(ValueError):
                T.verify(replace(self.t, **{attr: val}))
        with self.assertRaises(ValueError):
            T.verify(None)

    def test_nonmonic_or_bad_recurrences_rejected(self):
        """Malformed normalization cannot enter either moment-computation path."""
        with self.assertRaises(ValueError):
            T.power_sums((F(1), F(2)), 1)
        with self.assertRaises(ValueError):
            T.factor_coefficients((F(1), F(2)))
        with self.assertRaises(ValueError):
            T.logarithmic_moments((F(2), F(1)), 1)
        for count in (0, 17, True):
            with self.assertRaises(ValueError):
                T.power_sums(self.t.p_real, count)

    def test_shifted_matching_triangle(self):
        """All shifted blocks whose highest power lies in the shared jet also match."""
        t = self.t
        a, b = T.power_sums(t.p_real, 16), T.power_sums(t.p_nonreal, 16)
        for d in range(1, 9):
            for k in range(17-2*d):
                self.assertEqual([[a[k+i+j] for j in range(d)] for i in range(d)],
                                 [[b[k+i+j] for j in range(d)] for i in range(d)])

    def test_no_actual_xi_or_kernel_claim(self):
        """Synthetic root-disk proof premises are not recast as actual xi or full Lean."""
        p = T.payload(self.t)
        self.assertFalse(p['actual_xi'])
        self.assertFalse(p['full_analytic_lean_proof'])
        self.assertEqual(F(p['epsilon']), self.t.epsilon)


if __name__ == '__main__':
    unittest.main(verbosity=2)
