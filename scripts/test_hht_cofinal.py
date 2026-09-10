#!/usr/bin/env python3
"""Finite exact regressions; the infinite quantifiers are in the proof, not enumeration."""
from fractions import Fraction as F
import unittest
from hht_cofinal import (add,mul,inv,cpow,poly_mul,poly_eval,phase_basis,
    four_polynomials,circle_bound,pow_upper,threshold,phase_candidates,
    synthetic_certificate,positive_prefix_envelope,rat)

class CofinalTests(unittest.TestCase):
    def test_complex_arithmetic(self):
        z=(F(2,3),F(4,5)); self.assertEqual(mul(z,inv(z)),(1,0))
        self.assertEqual(cpow(z,3),mul(z,mul(z,z)))

    def test_multiplication_horner(self):
        p=[F(1),F(2),F(3)]; q=[F(-2),F(1)]; z=(F(1,3),F(2,5))
        self.assertEqual(poly_eval(poly_mul(p,q),z),mul(poly_eval(p,z),poly_eval(q,z)))

    def test_phase_interpolation(self):
        z=(F(2,5),F(1,5)); P,R=phase_basis([1,F(1,2)],z)
        self.assertEqual(poly_eval(P,z),(1,0));self.assertEqual(poly_eval(R,z),(0,1))
        for a in (F(1),F(1,2)):
            self.assertEqual(poly_eval(P,(a,0)),(0,0));self.assertEqual(poly_eval(R,(a,0)),(0,0))

    def test_conjugate_values(self):
        z=(F(2,5),F(1,5));P,R=phase_basis([1],z)
        self.assertEqual(poly_eval(P,(z[0],-z[1])),(1,0))
        self.assertEqual(poly_eval(R,(z[0],-z[1])),(0,-1))

    def test_four_fixed_phases(self):
        z=(F(2,5),F(1,5));P,R=phase_basis([1],z)
        self.assertEqual([poly_eval(p,z) for p in four_polynomials(P,R)],[(1,0),(0,1),(1,1),(1,-1)])

    def test_unit_circle_cover(self):
        # Rational parametrization; exact phase coverage, not trig samples.
        for t in [F(j,7) for j in range(-30,31)]:
            z=((1-t*t)/(1+t*t),2*t/(1+t*t))
            self.assertLess(min(phase_candidates(z)),-1)

    def test_pair_expression(self):
        phase=(F(3,5),F(4,5))
        ts=[(1,0),(0,1),(1,1),(1,-1)]
        self.assertEqual([2*mul(phase,mul(t,t))[0] for t in ts],phase_candidates(phase))

    def test_witness_may_switch(self):
        a=phase_candidates((F(1),F(0)));b=phase_candidates((F(-1),F(0)))
        self.assertNotEqual(a.index(min(a)),b.index(min(b)))

    def test_disk_majorant(self):
        p=[F(2),F(-3),F(4)];r=F(1,2);z=(F(3,10),F(4,10))
        x,y=poly_eval(p,z);self.assertLessEqual(x*x+y*y,circle_bound(p,r)**2)

    def test_directed_powers(self):
        for a in (F(0),F(1,3),F(7,8),F(99,100),F(1)):
            for k in (0,1,2,7,31,129):
                self.assertGreaterEqual(pow_upper(a,k,64),a**k)
                self.assertLessEqual(pow_upper(a,k,128),pow_upper(a,k,64))

    def test_strict_threshold(self):
        r=threshold(F(8),F(1,2),maximum=20)
        self.assertEqual(r['K'],4);self.assertEqual(r['upper'],F(1,2))

    def test_zero_and_small_budget(self):
        self.assertEqual(threshold(0,F(1,2))['K'],0)
        self.assertEqual(threshold(F(1,2),F(1,2))['K'],0)
        self.assertEqual(threshold(2,0)['K'],1)

    def test_exhaustion_is_inconclusive(self):
        self.assertIsNone(threshold(100,F(99,100),maximum=1))
        self.assertIsNone(threshold(1,F(1,2),maximum=0))

    def test_independent_single_anchor_envelope(self):
        C,a=positive_prefix_envelope([(F(1,2),F(1,2))],F(1,4),F(1,10))
        self.assertEqual((C,a),(F(1,5),F(1,2)))

    def test_two_anchor_direct_formula(self):
        C,a=positive_prefix_envelope([(F(1),F(1)),(F(2),F(2))],F(1,2),F(1,10))
        self.assertEqual(C,F(5,4));self.assertEqual(a,F(1,2))

    def test_overlap_gap_fail_closed(self):
        for boxes,r in [([(1,2),(2,3)],F(1,2)), ([(1,1)],1), ([(2,1)],F(1,2))]:
            with self.assertRaises(ValueError):positive_prefix_envelope(boxes,r,1)

    def test_input_contract(self):
        for x in (True,0.5,'1',1<<131073):
            with self.assertRaises(ValueError):rat(x)
        with self.assertRaises(ValueError):phase_basis([1,1],(1,1))
        with self.assertRaises(ValueError):phase_basis([1],(1,0))
        with self.assertRaises(ValueError):phase_candidates((1,1))
        with self.assertRaises(ValueError):inv((0,0))

    def test_bounded_exponents(self):
        for n in (-1,True,8193):
            with self.assertRaises(ValueError):cpow((1,1),n)
        with self.assertRaises(ValueError):pow_upper(F(3,2),2,64)
        with self.assertRaises(ValueError):threshold(1,1)
        with self.assertRaises(ValueError):circle_bound([1],-1)

    def test_synthetic_infinite_certificate(self):
        r=synthetic_certificate();self.assertEqual(r['K'],207);self.assertEqual(r['dimension'],10)
        self.assertLess(F(r['budget_upper']),1);self.assertFalse(r['actual_xi_counterexample'])
        for row in r['samples']:self.assertLess(F(row['normalized_upper']),0)

    def test_real_tail_mass_bound(self):
        # The proof uses integral comparison for the ENTIRE n>=9 tail.
        self.assertLess(sum((F(1,n*n) for n in range(9,200)),F(0)),F(1,8))

if __name__=='__main__':unittest.main(verbosity=2)
