#!/usr/bin/env python3
"""Exact finite regressions, not an infinite total-positivity proof."""
from fractions import Fraction as F
from itertools import product
import unittest
import hht_total_math as M


def moments(count=80):
    """Exact positive measure with six distinct support points."""
    return [sum(F(j, 7)**(n+1) for j in range(1, 7)) for n in range(count)]


class TotalTests(unittest.TestCase):
    def test_empty_determinant(self):
        self.assertEqual(M.determinant([]), 1)

    def test_pivots_and_swaps(self):
        self.assertEqual(M.determinant([[0, 2], [3, 4]]), -6)
        self.assertEqual(M.determinant([[1, 2], [2, 4]]), 0)

    def test_nonrational_and_bit_budget(self):
        for x in (True, 0.25, '1/4', 1 << 4097):
            with self.assertRaises(ValueError):
                M.determinant([[x]])

    def test_shapes_and_budget(self):
        for a in ([[1, 2]], [[1]*17 for _ in range(17)]):
            with self.assertRaises(ValueError):
                M.determinant(a)

    def test_index_contract(self):
        for ids in ((), (1, 1), (2, 1), (-1, 2), (True, 3), (0, 513), tuple(range(17))):
            with self.assertRaises(ValueError):
                M.indices(ids)

    def test_noncontiguous_selection(self):
        self.assertEqual(M.selected(list(range(30)), (0, 3), (2, 7), 4), [[6, 11], [9, 14]])

    def test_insufficient_data_and_shift(self):
        for ids, k in (((0, 8), 0), ((0, 1), True), ((0, 1), -1)):
            with self.assertRaises(ValueError):
                M.selected(list(range(10)), ids, ids, k)
        with self.assertRaises(ValueError):
            M.selected(list(range(10)), (0,), (0, 1))

    def test_lu_products_agree(self):
        mu = moments()
        for d in range(1, 6):
            a = M.selected(mu, tuple(range(d)), tuple(2*j for j in range(d)))
            ps = M.leading_positive_pivots(a)
            value = F(1)
            for p in ps:
                value *= p
            self.assertEqual(value, M.determinant(a))

    def test_lu_failure_is_not_zero_clipping(self):
        for a in ([[0]], [[-1]], [[1, 2], [2, 1]], [[1, 1], [1, 1]]):
            with self.assertRaises(ArithmeticError):
                M.leading_positive_pivots(a)

    def test_nonsymmetric_lu_does_not_prove_quadratic_positivity(self):
        a = [[F(1), F(10)], [F(0), F(1)]]
        self.assertEqual(M.leading_positive_pivots(a), [1, 1])
        self.assertLess(a[0][0]-a[0][1]-a[1][0]+a[1][1], 0)

    def test_positive_measure_all_small_minors(self):
        a = M.selected(moments(), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4))
        self.assertTrue(all(x > 0 for x in M.all_small_minors(a, 3)))

    def test_nonnegative_contiguous_is_not_general_fekete(self):
        a = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        solid = [M.determinant([row[j:j+d] for row in a[i:i+d]])
                 for d in range(1, 4) for i in range(4-d) for j in range(4-d)]
        self.assertTrue(all(x >= 0 for x in solid))
        self.assertTrue(any(x < 0 for x in M.all_small_minors(a, 2)))

    def test_tp2_does_not_lift_dimension(self):
        mu = [1, 2, 5, 14, 40]
        a = M.selected(mu, (0, 1, 2), (0, 1, 2))
        self.assertTrue(all(x > 0 for x in M.all_small_minors(a, 2)))
        self.assertEqual(M.determinant(a), -1)
        self.assertEqual(M.condensation_record(mu, 2)['defect'], -5)

    def test_condensation_grid(self):
        mu = moments()
        for d, k in product(range(1, 6), range(5)):
            z = M.condensation_record(mu, d, k)
            self.assertGreater(z['defect'], 0)
            self.assertEqual(M.next_dimension(z['left'], z['middle'], z['right'], z['lower']),
                             z['higher'])

    def test_condensation_singular_identity_but_no_division(self):
        mu = [F(1)]*16
        z = M.condensation_record(mu, 3)
        self.assertEqual(z['defect'], 0)
        with self.assertRaises(ValueError):
            M.next_dimension(z['left'], z['middle'], z['right'], z['lower'])

    def test_condensation_rejects_negative_denominator(self):
        for low in (0, -1):
            with self.assertRaises(ValueError):
                M.next_dimension(1, 3, 4, low)

    def test_general_gaps(self):
        mu = moments()
        for n, a, b in product(range(4), range(1, 7), range(1, 7)):
            self.assertGreater(mu[n]*mu[n+a+b]-mu[n+a]*mu[n+b], 0)

    def test_sparse_direction_matches_measure(self):
        exps, cs = (0, 3, 9, 17), (2, -3, 1, -5)
        for k in range(4):
            value = M.sparse_quadratic(moments(), exps, cs, k)
            direct = sum(F(j, 7)**(k+1)*sum(c*F(j, 7)**e for e, c in zip(exps, cs))**2
                         for j in range(1, 7))
            self.assertEqual(value, direct)
            self.assertGreater(value, 0)

    def test_zero_direction_is_not_strict(self):
        self.assertEqual(M.sparse_quadratic(moments(), (0, 8), (0, 0)), 0)
        with self.assertRaises(ValueError):
            M.sparse_quadratic(moments(), (0, 8), (1,))

    def test_empty_tau_and_order_contract(self):
        self.assertEqual(M.tau([], 0), 1)
        for d in (True, -1, 17):
            with self.assertRaises(ValueError):
                M.tau(moments(), d)
        for d in (0, 16, True):
            with self.assertRaises(ValueError):
                M.condensation_record(moments(), d)


if __name__ == '__main__':
    unittest.main(verbosity=2)
