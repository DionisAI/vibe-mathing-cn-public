#!/usr/bin/env python3
"""Exact regressions; do not replace real FLINT execution or Lean compilation."""
from fractions import Fraction as F
import unittest
from hht_shift_math import (anchor_budget,budget,first_certified_shift,grid_outer,positive_ldl)

class ShiftTests(unittest.TestCase):
    def test_single_anchor(self):
        c,a,M=anchor_budget([(F(1,2),F(1,2))],F(1,4),F(1))
        self.assertEqual((c,a,M),([F(2)],[F(1,2)],[F(1)]))
        self.assertEqual(first_certified_shift(c,a),2)
    def test_boundary_is_not_strict(self):
        self.assertEqual(budget([F(2)],[F(1,2)],1),1)
        self.assertIsNone(first_certified_shift([F(2)],[F(1,2)],1))
    def test_zero_tail(self):
        c,a,_=anchor_budget([(1,1),(2,2)],F(1,2),0)
        self.assertEqual(first_certified_shift(c,a),0)
    def test_budget_antitone(self):
        for d in range(1,11):
            cs=[F(i+1,3) for i in range(d)];aa=[F(i+1,d+2) for i in range(d)]
            for k in range(12):
                self.assertLessEqual(budget(cs,aa,k+1),budget(cs,aa,k))
    def test_exact_lagrange_disk_bounds(self):
        nodes=[F(1),F(1,2),F(1,3)];r=F(1,5)
        _,_,Ms=anchor_budget([(u,u) for u in nodes],r,1)
        # Rational complex multiplication, without a floating norm.
        for x,y in [(F(i,50),F(j,50)) for i in range(-5,6) for j in range(-5,6)]:
            self.assertLessEqual(x*x+y*y,r*r)
            for k,u in enumerate(nodes):
                re,im=F(1),F(0)
                for j,v in enumerate(nodes):
                    if j!=k:
                        re,im=(re*(x-v)-im*y)/(u-v),(im*(x-v)+re*y)/(u-v)
                self.assertLessEqual(re*re+im*im,Ms[k]**2)
    def test_interval_widening_is_conservative(self):
        exact=anchor_budget([(1,1),(2,2)],F(1,4),F(1,3))
        wide=anchor_budget([(F(99,100),F(101,100)),(F(199,100),F(201,100))],F(1,4),F(1,3))
        for k in range(8):self.assertGreaterEqual(budget(*wide[:2],k),budget(*exact[:2],k))
    def test_full_mass_monotonicity(self):
        small=anchor_budget([(1,1),(2,2)],F(1,4),1)
        large=anchor_budget([(1,1),(2,2)],F(1,4),2)
        for k in range(5):self.assertEqual(budget(*large[:2],k),2*budget(*small[:2],k))
    def test_bad_anchors(self):
        for boxes in ([],[(1,1)]*2,[(1,2),(2,3)],[(0,1)],[(2,1)],[(True,2)],[(1.0,2)],[(1,)],[(1,1)]*11):
            with self.assertRaises(ValueError):anchor_budget(boxes,F(1,4),1)
    def test_gap_and_tail_validation(self):
        for r,s in [(1,1),(2,1),(0,1),(-1,1),(F(1,4),-1),(0.1,1),(F(1,4),True)]:
            with self.assertRaises(ValueError):anchor_budget([(1,1)],r,s)
    def test_budget_validation(self):
        for c,a,k in [([1],[1],0),([-1],[F(1,2)],0),([1],[F(-1,2)],0),([1],[F(1,2)],True),([1],[F(1,2)],65),([1],[],0)]:
            with self.assertRaises(ValueError):budget(c,a,k)
    def test_bit_budget(self):
        with self.assertRaises(ValueError):anchor_budget([(1<<600,1<<600)],F(1,4),1)
    def test_outer_rounding(self):
        for i in range(-10,11):
            x=F(i,7);y=x+F(1,101);lo,hi=grid_outer(x,y,8)
            self.assertLessEqual(lo,x);self.assertGreaterEqual(hi,y)
            self.assertLess(x-lo,F(1,256));self.assertLess(hi-y,F(1,256))
    def test_ldl_good(self):
        self.assertEqual(positive_ldl([[F(2),F(1)],[F(1),F(2)]]),[F(2),F(3,2)])
    def test_ldl_refuses_wrong_sign_or_symmetry(self):
        for mat in ([],[[F(1),F(1)]],[[F(-1),F(0)],[F(0),F(-1)]],[[F(1),F(1)],[F(1),F(1)]],[[F(1),F(0)],[F(1),F(2)]]):
            with self.assertRaises((ValueError,ArithmeticError)):positive_ldl(mat)
    def test_weighted_interpolation_inequality(self):
        # Two anchors: exact Cauchy/interpolation comparison for complex points.
        for k in range(5):
            w=[F(1)**(k+1),F(1,2)**(k+1)]
            for aa in range(-3,4):
                for bb in range(-3,4):
                    x,y=F(1,10),F(1,20)
                    ell=[(2*x-1,2*y),(2-2*x,-2*y)]
                    values=[F(aa+bb),F(aa)+F(bb,2)]
                    energy=sum(t*t*z for t,z in zip(values,w))
                    kernel=sum((r*r+i*i)/z for (r,i),z in zip(ell,w))
                    self.assertLessEqual((aa+bb*x)**2+(bb*y)**2,energy*kernel)
    def test_maximum_exhaustion_is_not_refutation(self):
        self.assertIsNone(first_certified_shift([10**9],[F(99,100)],3))

if __name__=='__main__':unittest.main(verbosity=2)
