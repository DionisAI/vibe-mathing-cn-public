#!/usr/bin/env python3
"""Finite exact regressions for HHT-003; no finite test proves an infinite sum."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "fixtures" / "hankel_tail.py"
SPEC = importlib.util.spec_from_file_location("hankel_tail_fixture", PATH)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)
BASE = [(1, 0, 1), (2, 1, 1), (2, -1, 1)]
P = (F(2, 5), -F(7, 5), F(1))


def evaluate_real(p, x):
    """Independent direct-power evaluation for the real-tail test route."""
    return sum((F(c) * x**i for i, c in enumerate(p)), F(0))


def prefix_via_moments(nodes, p, k):
    """Independent binomial formula for moments, followed by matrix expansion."""
    from math import comb
    moments = []
    for n in range(k, k + 2 * len(p) - 1):
        power = n + 1
        value = F(0)
        for a, b, weight in nodes:
            a, b = F(a), F(b)
            real = sum(F(comb(power, 2*j)) * a**(power-2*j) *
                       (-1)**j * b**(2*j) for j in range(power//2 + 1))
            value += weight * real / (a*a + b*b)**power
        moments.append(value)
    return sum((F(ci) * F(cj) * moments[i+j]
                for i, ci in enumerate(p) for j, cj in enumerate(p)), F(0))


class HankelTailTests(unittest.TestCase):
    def test_power_count_bound(self):
        """Check the closed-form integral for a pure power counting envelope."""
        e = M.CountEnvelope(8, 3, F(1, 2))
        self.assertEqual(e.inverse_power(1), F(3, 4))
        self.assertEqual(e.inverse_power(2), F(1, 16))

    def test_log_count_bound(self):
        """Check the squared denominator contributed by the logarithmic term."""
        e = M.CountEnvelope(3, 5, F(1, 2), B=2, D=-3)
        self.assertEqual(e.inverse_power(2), F(49, 81))

    def test_finite_mass_and_empty_envelopes(self):
        """Alpha zero covers finite tail mass, including the identically empty tail."""
        self.assertEqual(M.CountEnvelope(2, 3, 0, D=-1).inverse_power(3), F(1, 4))
        self.assertEqual(M.CountEnvelope(2, 0, 0).inverse_power(1), 0)

    def test_subtracting_prefix_count_matters(self):
        """A negative D can sharpen a valid envelope without making it negative."""
        sharp = M.CountEnvelope(32, 1, F(1, 2), D=-1)
        crude = M.CountEnvelope(32, 1, F(1, 2))
        for s in range(1, 10):
            self.assertEqual(crude.inverse_power(s) - sharp.inverse_power(s), F(1, 32**s))

    def test_square_tail_integral_formula(self):
        """Recover the integral bound for an inverse-even-power series exactly."""
        for scale in (4, 8, 32):
            for included in range(1, 5):
                for s in range(1, 6):
                    e = M.square_tail_envelope(scale, included)
                    expected = F(1, scale**s * (2*s-1) * included**(2*s-1))
                    self.assertEqual(e.inverse_power(s), expected)

    def test_square_partial_sums_below_tail_bound(self):
        """Finite subsums are sanity checks, not a proof of the infinite bound."""
        for scale in (4, 8, 32):
            for included in range(1, 5):
                for s in range(1, 6):
                    actual = sum(F(1, (scale*n*n)**s)
                                 for n in range(included+1, included+33))
                    self.assertLess(actual, M.square_tail_envelope(scale, included).inverse_power(s))

    def test_known_finite_negative_prefix(self):
        """Recover the earlier rational negative witness before adding any tail."""
        self.assertEqual(M.exact_prefix_quadratic(BASE, P, 0, 3), -F(44, 3125))

    def test_prefix_two_algorithms(self):
        """Cross-check 60 exact quadratic forms by separate algebraic routes."""
        for nodes in (BASE, BASE + [(32, 0, 1)], [(3, 1, 2), (3, -1, 2)]):
            for p in (P, (1,), (0, 1), (1, -2, 0, 3)):
                for k in range(5):
                    self.assertEqual(M.exact_prefix_quadratic(nodes, p, k, 32),
                                     prefix_via_moments(nodes, p, k))

    def test_square_tail_quadratic_bound(self):
        """Bound 16 finite directional tails, including vanishing low coefficients."""
        for scale in (8, 32):
            for included in (1, 3):
                for p in (P, (1,), (0, 1), (1, -3, 2, -1)):
                    actual = sum(evaluate_real(p, F(1, scale*n*n))**2 / (scale*n*n)
                                 for n in range(included+1, included+21))
                    self.assertLess(actual, M.quadratic_tail_bound(
                        p, 0, M.square_tail_envelope(scale, included)))

    def test_matrix_bound_controls_complex_directions(self):
        """Check operator-bound implications without computing float eigenvalues."""
        nodes = [(4, 2, 1), (4, -2, 1), (5, 0, 1)]
        e = M.CountEnvelope(3, 3, 0)
        for p in ((1,), P, (1, -4, 2, 1), (0, 0, 1)):
            for k in range(4):
                actual = abs(M.exact_prefix_quadratic(nodes, p, k, 6))
                upper = M.matrix_tail_bound(len(p), k, e) * sum(F(c)**2 for c in p)
                self.assertLessEqual(actual, upper)

    def test_vanishing_can_certify_only_a_restricted_form(self):
        """Directional convergence must not be mislabeled as a defined full matrix."""
        e = M.CountEnvelope(2, 1, F(3, 2))
        self.assertEqual(M.quadratic_tail_bound((0, 1), 0, e), F(1, 4))
        with self.assertRaises(ValueError):
            M.matrix_tail_bound(2, 0, e)
        with self.assertRaises(ValueError):
            M.quadratic_tail_bound((1, 1), 0, e)

    def test_witness_scaling(self):
        """Rescaling a witness squares both its prefix and tail bound."""
        e = M.square_tail_envelope(32, 1)
        for factor in (-3, F(1, 2)):
            self.assertEqual(M.quadratic_tail_bound(tuple(factor*c for c in P), 0, e),
                             factor**2 * M.quadratic_tail_bound(P, 0, e))

    def test_exact_infinite_negative_certificate(self):
        """Freeze all rational numbers in the B=32, one-tail-node certificate."""
        c = M.synthetic_certificate(32, 1)
        self.assertEqual(c["prefix"], -F(1058239883, 104857600000))
        self.assertEqual(c["tail_bound"], F(203156669, 37748736000))
        self.assertEqual(c["upper"], -F(2222621111, 471859200000))
        self.assertEqual(c["decision"], "negative_under_stated_bounds")

    def test_simple_infinite_negative_margin(self):
        """Check the coarser pencil-and-paper bound based on p(x)<=2/5."""
        self.assertEqual(-F(44, 3125) + F(8, 25*32), -F(51, 12500))

    def test_uncontrolled_tail_can_reverse_sign(self):
        """Four positive tail nodes already reverse the B=8 prefix's sign."""
        nodes = BASE + [(8*n*n, 0, 1) for n in range(1, 5)]
        q = M.exact_prefix_quadratic(nodes, P, 0, 128)
        self.assertEqual(q, F(2167107684446717, 6340338096537600000))
        self.assertGreater(q, 0)
        # All remaining nodes are real positive, so their contributions are >=0.
        self.assertEqual(M.synthetic_certificate(8, 1)["decision"], "inconclusive")

    def test_prefix_uncertainty_can_block_certificate(self):
        """An approximate prefix needs a certified error smaller than its margin."""
        c = M.synthetic_certificate(32, 1)
        self.assertEqual(M.sign_certificate(c["prefix"], F(1, 100), c["tail_bound"])["decision"],
                         "inconclusive")

    def test_zero_margin_is_inconclusive(self):
        """Strict inequalities cannot be certified from an interval endpoint at zero."""
        self.assertEqual(M.sign_certificate(-1, F(1, 4), F(3, 4))["decision"], "inconclusive")
        self.assertEqual(M.sign_certificate(2, 0, 1)["decision"], "positive_under_stated_bounds")

    def test_invalid_envelopes_fail_closed(self):
        """Reject invalid cutoffs, negative growth and impossible nonnegative counts."""
        for args in ((0, 1, 0), (-1, 1, 0), (1, -1, 0), (1, 1, -1),
                     (1, 1, 0, -1), (1, 1, 0, 0, -2), (1.0, 1, 0), (True, 1, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                M.CountEnvelope(*args)

    def test_borderline_divergence_and_power_budgets(self):
        """The integral rule refuses s<=alpha instead of extrapolating through a pole."""
        e = M.CountEnvelope(1, 1, 2)
        for s in (-1, 0, 1, 2, True, 2.5, M.MAX_POWER+1):
            with self.assertRaises(ValueError):
                e.inverse_power(s)

    def test_invalid_polynomials_and_shifts(self):
        """Keep the witness search finite and all coefficients exact."""
        e = M.CountEnvelope(1, 1, 0)
        for p in ([], [0], [1.0], [True], "x", [1]*18, [1 << 300]):
            with self.assertRaises(ValueError):
                M.quadratic_tail_bound(p, 0, e)
        for k in (-1, True, 1.5, 33):
            with self.assertRaises(ValueError):
                M.quadratic_tail_bound(P, k, e)

    def test_invalid_prefix_nodes(self):
        """Reject zero nodes, cutoff violations and unpaired or misweighted roots."""
        for nodes in ([], [(0, 0, 1)], [(4, 0, 1)], [(2, 1, 1)],
                      [(2, 1, 1), (2, -1, 2)], [(1, 0, 0)], [(1, 0, True)],
                      [(1, 0)], [(1.0, 0, 1)], [(1, 0, 1)]*129):
            with self.subTest(nodes=nodes[:3]), self.assertRaises(ValueError):
                M.exact_prefix_quadratic(nodes, P, 0, 3)

    def test_duplicate_nodes_and_cutoff_equality(self):
        """Aggregate repeated entries and include real nodes exactly at the cutoff."""
        self.assertEqual(M.exact_prefix_quadratic([(2, 0, 1)]*2, (1,), 0, 2), 1)
        self.assertEqual(M.exact_prefix_quadratic([(2, 1, 1)]*2 + [(2, -1, 2)], P, 0, 3),
                         2 * M.exact_prefix_quadratic(BASE[1:], P, 0, 3))

    def test_invalid_certificates_and_square_tails(self):
        """Negative error bars and impossible finite-prefix budgets are rejected."""
        for args in ((-1, -1, 0), (-1, 0, -1), (-1.0, 0, 0),
                     (1 << (M.MAX_CERTIFICATE_BITS + 1), 0, 0)):
            with self.assertRaises(ValueError):
                M.sign_certificate(*args)
        for scale, included in ((0, 1), (-1, 1), (1, 0), (1, 126), (True, 1)):
            with self.assertRaises(ValueError):
                M.square_tail_envelope(scale, included)

    def test_sharper_envelope_and_larger_prefix(self):
        """The B=32 certificate remains negative after additional exact prefix work."""
        for included in (*range(1, 9), 32, 125):
            self.assertEqual(M.synthetic_certificate(32, included)["decision"],
                             "negative_under_stated_bounds")


if __name__ == "__main__":
    unittest.main(verbosity=2)
