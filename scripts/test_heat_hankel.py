#!/usr/bin/env python3
"""Finite exact tests for fixtures/heat_hankel.py; no canonical Result admission."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from itertools import product
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "fixtures" / "heat_hankel.py"
SPEC = importlib.util.spec_from_file_location("heat_hankel_fixture", PATH)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
GRID = tuple(product((F(1, 2), F(1), F(2)),
                     (F(1, 2), F(2), F(3)),
                     (F(1, 3), F(1), F(2))))


class HeatHankelTests(unittest.TestCase):
    def test_known_moments(self) -> None:
        self.assertEqual([M.moment(1, 2, 1, n) for n in range(5)],
                         [F(9, 5), F(31, 25), F(129, 125), F(611, 625), F(3049, 3125)])

    def test_two_moment_computations_agree(self) -> None:
        # 27 parameter triples x 13 orders = 351 exact identity checks.
        for a, b, c in GRID:
            with self.subTest(a=a, b=b, c=c):
                self.assertEqual(M.moments_from_log_derivative(a, b, c, 12),
                                 [M.moment(a, b, c, n) for n in range(13)])

    def test_shifted_determinant_family(self) -> None:
        # 27 triples x 9 shifts = 243 exact determinant checks, not a universal proof.
        for (a, b, c), k in product(GRID, range(9)):
            with self.subTest(a=a, b=b, c=c, k=k):
                computed = M.determinant(M.hankel(a, b, c, 3, k))
                self.assertEqual(computed, M.shifted_det_formula(a, b, c, k))
                self.assertLess(computed, 0)

    def test_known_counterexample_all_sampled_shifts(self) -> None:
        for k in range(17):
            self.assertEqual(M.determinant(M.hankel(1, 2, 1, 3, k)), -F(16, 5**(k+5)))

    def test_explicit_negative_quadratic_form(self) -> None:
        matrix = M.hankel(1, 2, 1, 3)
        vector = [F(2, 5), -F(7, 5), F(1)]
        self.assertEqual(sum(vector[i]*matrix[i][j]*vector[j]
                             for i in range(3) for j in range(3)), -F(44, 3125))

    def test_factorial_weighted_positive_definite_samples(self) -> None:
        # All leading minors of each d<=5, k<=5 matrix are positive (Sylvester).
        for d, k in product(range(1, 6), range(6)):
            with self.subTest(d=d, k=k):
                matrix = M.hankel(1, 2, 1, d, k, weighted=True)
                for size in range(1, d+1):
                    self.assertGreater(M.determinant([row[:size] for row in matrix[:size]]), 0)

    def test_fourth_heat_derivative_is_negative_at_zero(self) -> None:
        # Re((2-i)^4) = 2^4 - 6*2^2 + 1; no trig/float evaluation.
        self.assertEqual(1 + 2*(2**4 - 6*2**2 + 1), -13)

    def test_finite_spectrum_rank_bound(self) -> None:
        for a, b, c in GRID:
            self.assertEqual(M.determinant(M.hankel(a, b, c, 4)), 0)

    def test_equal_real_decay_is_not_a_degenerate_determinant(self) -> None:
        self.assertLess(M.determinant(M.hankel(1, 1, 1, 3)), 0)

    def test_invalid_parameters_fail_closed(self) -> None:
        for bad in (0, -1, 0.5, True, "1", 1 << 40, F(1, 1 << 40)):
            for position in range(3):
                values = [1, 2, 1]
                values[position] = bad
                with self.subTest(bad=bad, position=position), self.assertRaises(ValueError):
                    M.moment(*values, 0)

    def test_order_and_dimension_budgets(self) -> None:
        for bad in (-1, True, 0.5, 65):
            with self.assertRaises(ValueError):
                M.moment(1, 2, 1, bad)
            with self.assertRaises(ValueError):
                M.shifted_det_formula(1, 2, 1, bad)
        for bad in (0, -1, True, 1.5, 9):
            with self.assertRaises(ValueError):
                M.hankel(1, 2, 1, bad)
        with self.assertRaises(ValueError):
            M.hankel(1, 2, 1, 3, 64)
        with self.assertRaises(ValueError):
            M.hankel(1, 2, 1, 3, weighted="yes")

    def test_elimination_pivots_and_bad_matrices(self) -> None:
        self.assertEqual(M.determinant([[0, 1], [1, 0]]), -1)
        self.assertEqual(M.determinant([[1, 2], [2, 4]]), 0)
        for matrix in ([], [[1, 2]], [[0.5]], [[True]]):
            with self.assertRaises(ValueError):
                M.determinant(matrix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
