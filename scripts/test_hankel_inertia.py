#!/usr/bin/env python3
"""Exact finite regressions. Test PASS is not theorem admission or novelty evidence."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import random
import unittest

PATH = Path(__file__).resolve().parents[1] / "fixtures" / "hankel_inertia.py"
SPEC = importlib.util.spec_from_file_location("hankel_inertia_fixture", PATH)
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)
TWO_PAIRS = [(1, 0, 1), (3, 1, 1), (3, -1, 1), (4, 1, 1), (4, -1, 1)]
CASES = [
    [(1, 0, 1)],
    [(1, 0, 1), (2, 0, 1), (3, 0, 1)],
    [(2, 1, 1), (2, -1, 1)],
    [(1, 0, 1), (2, 1, 1), (2, -1, 1)],
    TWO_PAIRS,
    [(1, 0, 2), (3, 1, 3), (3, -1, 3)],
    [(-2, 0, 2), (1, 0, 1), (3, 1, 1), (3, -1, 1)],
    [(0, 1, 1), (0, -1, 1)],
    [(0, 1, 1), (0, -1, 1), (0, 2, 1), (0, -2, 1)],
    [(F(1, 2), 0, 1), (F(3, 2), F(1, 3), 2), (F(3, 2), -F(1, 3), 2)],
]


def quadratic(matrix, vector):
    return sum(vector[i]*matrix[i][j]*vector[j]
               for i in range(len(vector)) for j in range(len(vector)))


def pair_block_matrix(spectrum, d, k):
    """Reconstruct from real 1x1 and conjugate 2x2 blocks, not moment entries."""
    result = [[F(0) for _ in range(d)] for _ in range(d)]
    for node, weight in H.canonical(spectrum):
        if node[1] < 0:
            continue
        u = H.reciprocal(node)
        powers = [H.power(u, j) for j in range(d)]
        w = H.power(u, k+1)
        for i in range(d):
            for j in range(d):
                x, y = powers[i]
                v, z = powers[j]
                if node[1] == 0:
                    result[i][j] += weight*w[0]*x*v
                else:
                    result[i][j] += 2*weight*(w[0]*(x*v-y*z)-w[1]*(x*z+y*v))
    return result


def charpoly_inertia(matrix):
    """Independent exact spectral count via Faddeev-LeVerrier and sign variations.

Real symmetric matrices have only real eigenvalues, so Descartes counts are exact.
This is a test oracle, not the symmetric-elimination algorithm being tested.
"""
    n = len(matrix)
    a = [[F(x) for x in row] for row in matrix]
    b = [[F(i == j) for j in range(n)] for i in range(n)]
    coefficients = [F(1)]
    for degree in range(1, n+1):
        b = [[sum(a[i][h]*b[h][j] for h in range(n))
              for j in range(n)] for i in range(n)]
        coefficient = -sum(b[i][i] for i in range(n))/degree
        coefficients.append(coefficient)
        for i in range(n):
            b[i][i] += coefficient
    def variations(values):
        signs = [1 if x > 0 else -1 for x in values if x]
        return sum(x != y for x, y in zip(signs, signs[1:]))
    positive = variations(coefficients)
    negative = variations([c*(-1)**(n-i) for i, c in enumerate(coefficients)])
    return positive, negative, n-positive-negative


class HankelInertiaTests(unittest.TestCase):
    def test_moment_routes_agree(self):
        for spectrum in CASES:
            self.assertEqual(H.moments(spectrum, 16), H.moments_from_polynomial(spectrum, 16))

    def test_full_inertia_270_cases(self):
        for case, spectrum in enumerate(CASES):
            n = len(H.canonical(spectrum))
            for d in range(n, n+3):
                for k in range(9):
                    with self.subTest(case=case, d=d, k=k):
                        self.assertEqual(H.inertia(H.hankel(spectrum, d, k)),
                                         H.predicted_inertia(spectrum, d, k))

    def test_real_block_identity(self):
        for spectrum in CASES:
            n = len(H.canonical(spectrum))
            for k in (0, 1, 4):
                self.assertEqual(pair_block_matrix(spectrum, n+1, k),
                                 H.hankel(spectrum, n+1, k))

    def test_hht001_formula_regression(self):
        spectrum = [(1, 0, 1), (2, 1, 1), (2, -1, 1)]
        for k in range(9):
            self.assertEqual(H.determinant(H.hankel(spectrum, 3, k)), -F(16, 5**(k+5)))

    def test_even_pairs_positive_determinant(self):
        for k in range(9):
            matrix = H.hankel(TWO_PAIRS, 5, k)
            self.assertEqual(H.determinant(matrix), F(1, 118587876497000*170**k))
            self.assertEqual(H.inertia(matrix), (3, 2, 0))

    def test_integer_negative_witness(self):
        vector = [44, -411, 1235, -1123, 255]
        self.assertEqual(quadratic(H.hankel(TWO_PAIRS, 5), vector), -F(375, 16))
        for node, _ in H.canonical(TWO_PAIRS):
            value = H.ZERO
            for j, coefficient in enumerate(vector):
                term = H.power(H.reciprocal(node), j)
                value = H.add(value, (coefficient*term[0], coefficient*term[1]))
            expected = (F(0), -F(25, 4)*node[1]) if node[0] == 3 else H.ZERO
            self.assertEqual(value, expected)

    def test_multiplicity_is_not_distinct_rank(self):
        spectrum = CASES[5]  # degree 8, but only 3 distinct nodes
        self.assertEqual(H.inertia(H.hankel(spectrum, 8)), (2, 1, 5))
        split = [(1, 0, 1), (1, 0, 1), (3, 1, 1), (3, 1, 2), (3, -1, 3)]
        self.assertEqual(H.moments(spectrum, 12), H.moments(split, 12))

    def test_negative_real_parity(self):
        spectrum = [(-2, 0, 1), (1, 0, 1), (3, 1, 1), (3, -1, 1)]
        self.assertEqual(H.inertia(H.hankel(spectrum, 4, 0)), (2, 2, 0))
        self.assertEqual(H.inertia(H.hankel(spectrum, 4, 1)), (3, 1, 0))

    def test_zero_diagonal_requires_two_by_two_pivot(self):
        self.assertEqual(H.inertia([[0, 2], [2, 0]]), (1, 1, 0))
        self.assertEqual(H.inertia([[0, 2, 3], [2, 0, 4], [3, 4, 0]]), (1, 2, 0))
        self.assertEqual(H.inertia(H.hankel(CASES[7], 2)), (1, 1, 0))

    def test_zero_and_singular_matrices(self):
        self.assertEqual(H.inertia([[0, 0], [0, 0]]), (0, 0, 2))
        self.assertEqual(H.inertia([[1, 2], [2, 4]]), (1, 0, 1))
        self.assertEqual(H.inertia([[-1, -2], [-2, -4]]), (0, 1, 1))
        self.assertEqual(H.determinant([[0, 1], [1, 0]]), -1)

    def test_exact_congruence_regressions(self):
        rng = random.Random(20260908)
        for d in range(1, 9):
            for trial in range(5):
                signs = [rng.choice((-1, 0, 1)) for _ in range(d)]
                p = [[F(1) if i == j else F(rng.randint(-3, 3)) if i < j else F(0)
                      for j in range(d)] for i in range(d)]
                matrix = [[sum(signs[h]*p[h][i]*p[h][j] for h in range(d))
                           for j in range(d)] for i in range(d)]
                with self.subTest(d=d, trial=trial):
                    self.assertEqual(H.inertia(matrix),
                                     (signs.count(1), signs.count(-1), signs.count(0)))
                    self.assertEqual(H.inertia(matrix), charpoly_inertia(matrix))

    def test_characteristic_polynomial_oracle_on_spectra(self):
        for spectrum in CASES:
            n = len(H.canonical(spectrum))
            for k in (0, 1):
                matrix = H.hankel(spectrum, n, k)
                self.assertEqual(H.inertia(matrix), charpoly_inertia(matrix))

    def test_all_shift_rational_bound(self):
        bounds = H.hiding_bounds(2, 2, 128)
        self.assertEqual(bounds["lower_bound"], F(1, 21))
        self.assertEqual(bounds["perturbation_bound"], F(16385, 524288))
        self.assertEqual(bounds["margin"], F(180203, 11010048))
        self.assertTrue(bounds["all_shift_positive"])
        self.assertTrue(bounds["heat_positive"])
        self.assertFalse(H.hiding_bounds(2, 2, 2)["all_shift_positive"])
        self.assertFalse(H.hiding_bounds(2, 2, 2)["heat_positive"])

    def test_hidden_pairs_small_blocks_and_margin(self):
        spectrum = H.hiding_spectrum(2, 2, 128)
        margin = H.hiding_bounds(2, 2, 128)["margin"]
        for d in (1, 2):
            for k in (*range(17), 50):
                matrix = H.hankel(spectrum, d, k)
                self.assertEqual(H.inertia(matrix), (d, 0, 0))
                difference = [[matrix[i][j] - (F(1, 2)**k*margin if i == j else 0)
                               for j in range(d)] for i in range(d)]
                self.assertEqual(H.inertia(difference), (d, 0, 0))

    def test_hidden_pairs_full_size_is_indefinite(self):
        spectrum = H.hiding_spectrum(2, 2, 128)
        for k in (0, 1, 2, 8):
            self.assertEqual(H.inertia(H.hankel(spectrum, 6, k)), (4, 2, 0))
            self.assertGreater(H.determinant(H.hankel(spectrum, 6, k)), 0)
        self.assertEqual(H.inertia(H.hankel(spectrum, 8)), (4, 2, 2))

    def test_factorial_weighted_positive_samples(self):
        for spectrum in (TWO_PAIRS, H.hiding_spectrum(2, 2, 128)):
            for d in range(1, 6):
                for k in range(4):
                    self.assertEqual(H.inertia(H.hankel(spectrum, d, k, weighted=True)), (d, 0, 0))

    def test_general_hiding_parameters(self):
        for d, q, b in ((1, 3, 128), (2, 1, 128), (3, 2, 1 << 18)):
            bounds = H.hiding_bounds(d, q, b)
            self.assertTrue(bounds["all_shift_positive"])
            self.assertTrue(bounds["heat_positive"])
            spectrum = H.hiding_spectrum(d, q, b)
            self.assertEqual(H.inertia(H.hankel(spectrum, d+2*q)), (d+q, q, 0))

    def test_incomplete_or_invalid_spectra_rejected(self):
        bad = ([], [(0, 0, 1)], [(1, 1, 1)], [(1, 1, 1), (1, -1, 2)],
               [(1, 0, 0)], [(True, 0, 1)], [(1.0, 0, 1)], [(1, 0, True)],
               [(1 << 40, 0, 1)], [(1, 0, 33)], [(1, 2)], "spectrum",
               [(i, 0, 1) for i in range(1, 14)])
        for spectrum in bad:
            with self.subTest(spectrum=spectrum), self.assertRaises(ValueError):
                H.moments(spectrum, 0)

    def test_order_dimension_and_scope_limits(self):
        for bad in (-1, 65, True, 1.5):
            with self.assertRaises(ValueError):
                H.moments(CASES[0], bad)
        for bad in (0, 13, True, 1.5):
            with self.assertRaises(ValueError):
                H.hankel(CASES[0], bad)
        with self.assertRaises(ValueError):
            H.hankel(CASES[0], 3, 64)
        with self.assertRaises(ValueError):
            H.hankel(CASES[0], 1, weighted="yes")
        with self.assertRaises(ValueError):
            H.predicted_inertia(TWO_PAIRS, 3)
        for args in ((2, 0, 128), (2, 6, 128), (2, 2, 0), (2, 2, 1 << 21)):
            with self.assertRaises(ValueError):
                H.hiding_bounds(*args)

    def test_invalid_matrices_rejected(self):
        for matrix in ([], [[1, 2]], [[True]], [[1.0]], [[1 << 17000]], "matrix"):
            with self.assertRaises(ValueError):
                H.inertia(matrix)
        with self.assertRaises(ValueError):
            H.inertia([[1, 2], [3, 4]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
