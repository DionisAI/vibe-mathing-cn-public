#!/usr/bin/env python3
"""Finite rational regressions on positive and indefinite sequence models."""
from fractions import Fraction as F
from itertools import product
import unittest
import hht_coefficient_cone as C
import hht_balance as M


class BalanceTests(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(M.distance_squared(F(-1),F(0),F(2)), 1)
        self.assertEqual(M.distance_squared(F(1),F(0),F(2)), 0)
        self.assertEqual(M.distance_squared(F(4),F(0),F(2)), 4)
        with self.assertRaises(ValueError): M.distance_squared(1,2,0)

    def test_exact_rectangle_minimum(self):
        for c,ua,ub,va,vb in ((1,0,0,0,2),(1,3,8,0,2),(1,0,2,3,4),
                             (2,1,4,0,1),(1,2,2,3,3)):
            c,ua,ub,va,vb=map(F,(c,ua,ub,va,vb))
            u=min(max(vb-c,ua),ub);v=min(max(c,va),vb)
            value=(c-v)**2+u*u+2*(c-vb)*u
            self.assertEqual(M.rectangle_bound(c,ua,ub,va,vb),value)
            for i,j in product(range(11),repeat=2):
                x=ua+(ub-ua)*i/10;y=va+(vb-va)*j/10
                self.assertLessEqual(value,(c-y)**2+x*x+2*(c-vb)*x)

    def test_rescued_family_all_sampled_sizes(self):
        for n in (1,2,5,10,25,64,128):
            p=M.rescued_family(n)
            self.assertEqual(C.classify(p)['status'],'uncovered')
            r=M.classify_balance(p)
            self.assertEqual(r['status'],'conditional_strict_positive')
            self.assertEqual(r['sign_changes'],2*n-1)
            self.assertEqual(r['opposite_mass_interval'][1],'2')
            self.assertGreaterEqual(F(r['lower_multiplier']),F(498624,390625))

    def test_radius_and_lower_ratio_validation(self):
        for lo,hi in ((0,1),(-1,1),(2,1),(True,1),(0.5,1),(1,False)):
            with self.assertRaises(ValueError): M.classify_balance([(0,1)],lo,hi)
        for box in ((0,0,1,0,1),(1,2,1,0,1),(1,0,1,-1,1)):
            with self.assertRaises(ValueError): M.rectangle_bound(*box)

    def test_grid_on_indefinite_sequence(self):
        # 625 patterns x 3 shifts, with independent signed-atomic checks.
        mu=[C.boundary_moment(i) for i in range(12)]
        low=mu[1]/mu[0]
        counts={'positive':0,'inconclusive':0}
        for cs in product((-4,-1,0,1,4),repeat=4):
            p=[(0,1)]+list(enumerate(cs,start=1))
            r=M.classify_balance(p,low,1);bound=F(r['lower_multiplier'])
            counts['positive' if bound>0 else 'inconclusive']+=1
            for k in range(3):
                q=C.quadratic_form(mu,p,k)
                self.assertEqual(q,C.spectral_form([1,F(1,2),F(1,4)],
                                                   [1,1,-F(1,2)],p,k))
                self.assertGreaterEqual(q,mu[k]*bound)
        self.assertGreater(counts['positive'],0)
        self.assertGreater(counts['inconclusive'],0)

    def test_negative_witness_remains_uncovered(self):
        p=[(0,F(1,2)),(1,-F(3,2)),(2,1)]
        r=M.classify_balance(p,F(39,44),1)
        self.assertLess(F(r['lower_multiplier']),0)
        self.assertEqual(r['status'],'inconclusive')
        self.assertFalse(r['negative_bound_is_counterexample'])

    def test_old_cone_bounds_not_degraded(self):
        for cs in product((-F(1,4),0,F(1,4)),repeat=4):
            p=[(0,1)]+list(enumerate(cs,start=1))
            old=C.classify(p,1);new=M.classify_balance(p,F(1,2),1)
            self.assertGreaterEqual(F(new['lower_multiplier']),F(old['lower_multiplier']))

    def test_rescaling_negation_and_exponent_shift(self):
        p=M.rescued_family(4)
        a=M.classify_balance(p)
        self.assertEqual(a,M.classify_balance([(e,-v) for e,v in p]))
        b=M.classify_balance([(e+3,7*v) for e,v in p])
        self.assertEqual(F(b['lower_multiplier']),49*F(a['lower_multiplier']))
        self.assertEqual(b['anchor'],'mu_(k+6)')

    def test_equality_is_not_strict(self):
        r=M.classify_balance([(0,1),(1,-2)],F(1,2),F(1,2))
        self.assertEqual(r['status'],'conditional_nonnegative')
        self.assertEqual(r['lower_multiplier'],'0')

    def test_larger_interval_cannot_improve_bound(self):
        for p in (M.rescued_family(2,1),[(0,1),(1,-3),(2,4)]):
            tight=M.classify_balance(p,F(3,4),1)
            wide=M.classify_balance(p,F(1,2),1)
            self.assertLessEqual(F(wide['lower_multiplier']),F(tight['lower_multiplier']))

    def test_dense_scaled_indefinite_model(self):
        p=M.rescued_family(25)
        R=M.XI_RADIUS
        mu=[R**(n+1)*C.boundary_moment(n) for n in range(108)]
        bound=F(M.classify_balance(p)['lower_multiplier'])
        for k in (0,7):
            q=C.quadratic_form(mu,p,k)
            self.assertEqual(q,C.quadratic_convolution(mu,p,k))
            self.assertGreaterEqual(q,mu[k]*bound)

    def test_generic_flags_and_invalid_family(self):
        r=M.classify_balance([(0,1)])
        self.assertFalse(r['sequence_premises_verified_here'])
        self.assertFalse(r['rh_proved'])
        for n in (0,-1,True,129):
            with self.assertRaises(ValueError): M.rescued_family(n)
        for s in (0,True,1025):
            with self.assertRaises(ValueError): M.rescued_family(1,s)

if __name__=='__main__': unittest.main(verbosity=2)
