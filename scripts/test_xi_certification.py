#!/usr/bin/env python3
"""Offline regressions for certificate plumbing, not substitute special-function proofs."""
from fractions import Fraction as F
from pathlib import Path
import unittest
import certify_xi_prefix as C


class CertificationTests(unittest.TestCase):
    def test_brackets(self):
        """The intended ten open intervals are disjoint and within the cutoff."""
        self.assertEqual(len(C.check_brackets(C.BRACKETS, 50)), 10)

    def test_bad_brackets(self):
        """Overlaps, duplicates, ordering errors, floats and booleans are rejected."""
        for brackets in ([], [(14, 15), (14, 15)], [(21, 22), (14, 15)],
                         [(14, 16), (15, 17)], [(0, 1)], [(49, 51)],
                         [(1, 1)], [(True, 2)], [(14.0, 15)], [(14, 15, 16)]):
            with self.subTest(brackets=brackets), self.assertRaises(ValueError):
                C.check_brackets(brackets, 50)

    def test_touching_open_intervals(self):
        """A shared nonzero endpoint does not identify two interior roots."""
        self.assertEqual(C.check_brackets([(48, 49), (49, 50)], 50),
                         ((48, 49), (49, 50)))

    def test_cover_logic(self):
        """Sign changes and matching total count jointly exhaust multiplicities."""
        C.check_cover_logic([(14, 15), (21, 22)], 50,
                            {14: 1, 15: -1, 21: -1, 22: 1}, 2)

    def test_count_mismatch(self):
        """Found critical-line roots are not enough when the total count is larger."""
        for count in (0, 3, True, F(2)):
            with self.assertRaises(ValueError):
                C.check_cover_logic([(14, 15), (21, 22)], 50,
                                    {14: 1, 15: -1, 21: -1, 22: 1}, count)

    def test_sign_uncertainty(self):
        """An interval containing zero, a missing endpoint or bool cannot certify a sign."""
        for signs in ({14: 0, 15: -1}, {14: True, 15: -1}, {14: 1}, {14: 1, 15: 1}):
            with self.assertRaises(ValueError):
                C.check_cover_logic([(14, 15)], 50, signs, 1)

    def test_positive_ldl(self):
        """Exact reference examples reproduce known Schur pivots."""
        self.assertEqual(C.positive_ldl([[F(2), F(1)], [F(1), F(2)]]), [F(2), F(3, 2)])
        for n in range(1, 9):
            self.assertEqual(C.positive_ldl([[F(int(i == j)) for j in range(n)]
                                             for i in range(n)]), [F(1)] * n)

    def test_positive_determinant_not_enough(self):
        """Two negative directions give positive determinant but must be rejected."""
        with self.assertRaises(ArithmeticError):
            C.positive_ldl([[F(-1), F(0)], [F(0), F(-1)]])

    def test_ldl_zero_and_shape(self):
        """Singular, empty and nonsquare inputs cannot certify strict positivity."""
        with self.assertRaises(ArithmeticError):
            C.positive_ldl([[F(1), F(1)], [F(1), F(1)]])
        for m in ([], [[1, 2]], [[1] * 17 for _ in range(17)]):
            with self.assertRaises(ValueError):
                C.positive_ldl(m)

    def test_rational_interval_margin(self):
        """The old coarse intervals really imply the claimed arithmetic lower bound."""
        bound = F(1, 225) * F(1, 484) * (F(1, 225) - F(1, 441))**2 / (F(1, 196) + F(1, 441))
        self.assertEqual(bound, F(64, 10838953125))
        self.assertEqual(bound - F(29, 4784677734375), F(4035853, 684208916015625))

    def test_square_completion(self):
        """Finite exact algebra checks agree with the separately compiled real theorem."""
        for x in (F(1, 2), F(1), F(2)):
            for y in (F(-2), F(0), F(1, 3)):
                for a in (F(-1), F(0), F(3)):
                    for b in (F(-2), F(0), F(1)):
                        q = x*a*a + (x*x-y*y)*2*a*b + (x**3-3*x*y*y)*b*b
                        loss = (x*x+y*y)/x*y*y
                        self.assertEqual(x*(q+b*b*loss), (x*(a+b*x)-y*b*y)**2)
                        self.assertGreaterEqual(q, -b*b*loss)

    def test_all_lean_theorems_audited(self):
        """Every source theorem has an audit request; this test does not compile Lean."""
        import re
        source = (Path(__file__).resolve().parents[1] / 'fixtures/lean-proof/HHTInfinite.lean').read_text()
        names = re.findall(r'^theorem\s+(\w+)', source, re.M)
        self.assertEqual(len(names), 8)
        for name in names:
            self.assertEqual(source.count('#print axioms HHT005.' + name + '\n'), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
