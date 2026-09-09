#!/usr/bin/env python3
"""Exact finite regressions; infinite conclusions use the documented bounds."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from itertools import product
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('hht_localization', ROOT/'fixtures/hankel_localization.py')
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = H
SPEC.loader.exec_module(H)


class LocalizationTests(unittest.TestCase):
    def test_target_mapping(self):
        """The chosen target really maps from a noncentral critical-strip point."""
        s = H.square_spectrum()
        self.assertEqual(s.target, (F(560,1369),F(192,1369)))
        self.assertEqual(H.mul(s.target,(F(35,16),-F(3,4))), (1,0))

    def test_normalization_all_tested_powers(self):
        """Recover p(u*)=i and p(conj(u*))=-i by exact Horner evaluation."""
        for M in range(13):
            s=H.square_spectrum(); c=s.witness(M); x,y=s.target
            self.assertEqual(H.evaluate(c['coefficients'],(x,y)),(0,1))
            self.assertEqual(H.evaluate(c['coefficients'],(x,-y)),(0,-1))

    def test_general_head_annihilation(self):
        """An extra conjugate pair and real nodes are all killed, not ignored."""
        s=H.Localization((F(1,3),F(1,5)),
            ((1,0),(F(1,2),F(1,7)),(F(1,2),-F(1,7))),F(1,10),1)
        for M in range(5):
            c=s.witness(M)
            self.assertTrue(all(H.evaluate(c['coefficients'],u)==(0,0) for u in s.head))

    def test_uniform_and_direct_bounds(self):
        """The coefficient-specific majorant never exceeds its geometric bound."""
        for g,d,M in product((F(3,2),F(5,2),F(7,2)),(F(1,8),F(1,4)),range(8)):
            c=H.square_spectrum(g,d).witness(M)
            self.assertLessEqual(c['direct_tail_bound'],c['geometric_tail_bound'])

    def test_four_terminating_certificates(self):
        """Increasing target height changes the sufficient witness dimension."""
        for g,M,dim in ((F(3,2),5,8),(F(5,2),12,16),(F(9,2),32,38),(F(17,2),98,108)):
            c=H.square_spectrum(g).find_witness()
            self.assertEqual((c['power'],c['dimension']),(M,dim))
            self.assertLess(c['full_upper'],0)
            self.assertEqual(c['decision'],'negative_under_stated_bounds')

    def test_frozen_first_certificate(self):
        """Freeze exact constants and a full infinite upper bound, not decimals."""
        c=H.square_spectrum().find_witness()
        self.assertEqual(c['theta'],F(1369,4096))
        self.assertEqual(c['eta'],F(1120,1369))
        self.assertEqual(c['C'],F(14570821445,105906176))
        self.assertEqual(c['full_upper'], -F(122520272068206457337249448421055,
                                           151945680414436301673920458653696))

    def test_finite_tail_sanity_below_infinite_bound(self):
        """A finite tail is checked against, never substituted for, the envelope."""
        for M in range(7):
            c=H.square_spectrum().witness(M)
            tail=H.real_square_partial(c['coefficients'],2,10)
            self.assertGreaterEqual(tail,0)
            self.assertLessEqual(tail,c['direct_tail_bound'])

    def test_conjugate_pair_negative(self):
        """Normalized complex squaring has a minus sign unlike modulus squaring."""
        s=H.square_spectrum(); c=s.find_witness(); total=F(0)
        for z in (s.target,(s.target[0],-s.target[1])):
            val=H.evaluate(c['coefficients'],z)
            total += H.mul(z,H.mul(val,val))[0]
        self.assertEqual(total,-c['eta'])

    def test_moment_and_evaluation_routes(self):
        """Check 6 directions through a dense moment matrix and direct evaluations."""
        s=H.square_spectrum()
        nodes=(*s.head,s.target,(s.target[0],-s.target[1]),(F(1,4),F(0)))
        for M in range(6):
            p=s.witness(M)['coefficients']
            mu=[sum((H.power(z,j+1)[0] for z in nodes),F(0)) for j in range(2*len(p)-1)]
            matrix=sum((ci*cj*mu[i+j] for i,ci in enumerate(p) for j,cj in enumerate(p)),F(0))
            direct=sum((H.mul(z,H.mul(H.evaluate(p,z),H.evaluate(p,z)))[0] for z in nodes),F(0))
            self.assertEqual(matrix,direct)

    def test_complex_tail_pointwise_bound(self):
        """Bound a genuine complex tail, rather than only positive real tail nodes."""
        s=H.square_spectrum(); r=s.tail_radius
        for M,z in product(range(5),((r/2,r/3),(r/3,-r/4),(r/5,r/2))):
            c=s.witness(M); val=H.evaluate(c['coefficients'],z)
            major=r**(2*M)*c['A_bound']**2*(abs(c['a'])+r*abs(c['b']))**2
            self.assertLessEqual(val[0]**2+val[1]**2,major)

    def test_empty_tail_and_empty_head(self):
        """Finite spectra are covered without inventing tail mass."""
        s=H.Localization((1,1),(),F(1,2),0)
        c=s.find_witness()
        self.assertEqual(c['power'],0)
        self.assertEqual(c['full_upper'],-2)
        self.assertEqual(c['coefficients'],(-F(1),F(1)))

    def test_multiplicity_only_changes_target_margin(self):
        """Positive target multiplicity is a weight, not an extra distinct node."""
        s=H.square_spectrum()
        s3=H.Localization(s.target,s.head,s.tail_radius,s.tail_mass,3)
        c,c3=s.witness(2),s3.witness(2)
        self.assertEqual(c3['coefficients'],c['coefficients'])
        self.assertEqual(c3['eta'],3*c['eta'])
        self.assertEqual(c3['direct_tail_bound'],c['direct_tail_bound'])

    def test_strict_margin_and_budget(self):
        """Equality is not negative and finite exhaustion is not a proof of PSD."""
        self.assertEqual(H.first_power(1,F(1,2),1,1),(1,F(1,2)))
        with self.assertRaises(ArithmeticError): H.first_power(1,F(1,2),1,0)
        with self.assertRaises(ArithmeticError): H.square_spectrum().find_witness(0)
        self.assertEqual(H.first_power(0,0,1),(0,0))

    def test_structural_validation_never_proves_tail_truth(self):
        """A fabricated but well-shaped external tail premise stays conditional."""
        s=H.Localization((1,1),(),F(1,4),0)
        self.assertFalse(s.find_witness()['tail_premises_verified_by_structure'])

    def test_bad_targets_and_heads(self):
        """Reject real/zero targets, duplicates and incomplete conjugate heads."""
        for target in ((1,0),(0,1),(-1,1),(1,-1),(0,0),(True,1),(0.5,1)):
            with self.subTest(target=target),self.assertRaises(ValueError):
                H.Localization(target,(),F(1,4),1)
        for head in (((1,1),),((1,-1),),((2,1),),((2,0),(2,0)),((0,0),)):
            with self.subTest(head=head),self.assertRaises(ValueError):
                H.Localization((1,1),head,F(1,4),1)

    def test_bad_radius_mass_and_counts(self):
        """No zero gap, negative mass, implicit booleans or unbounded resources."""
        for r,S in ((0,1),(2,1),(-1,1),(F(1,4),-1),(True,1),(0.5,1)):
            with self.assertRaises(ValueError): H.Localization((1,1),(),r,S)
        for m in (0,True,-1,1025):
            with self.assertRaises(ValueError): H.Localization((1,1),(),F(1,4),1,m)
        for M in (-1,True,0.5,257):
            with self.assertRaises(ValueError): H.square_spectrum().witness(M)
        with self.assertRaises(ValueError): H.rational(1<<80)

    def test_bad_square_spectrum_and_search(self):
        """Synthetic family restrictions are enforced before any certificate."""
        for g,d in ((1,F(1,4)),(F(3,2),0),(F(3,2),1),(F(199,100),F(1,2)),(F(35,2),F(1,4))):
            with self.assertRaises(ValueError): H.square_spectrum(g,d)
        for C,t,e in ((-1,F(1,2),1),(1,1,1),(1,-1,1),(1,F(1,2),0),(1,0.5,1)):
            with self.assertRaises(ValueError): H.first_power(C,t,e)

    def test_telescoping_mass_majorant(self):
        """Finite sanity checks for the separately proved sum_{n>N}1/n^2<=1/N."""
        for N in range(1,9):
            finite=sum((F(1,n*n) for n in range(N+1,65)),F(0))
            telescope=sum((F(1,n*(n-1)) for n in range(N+1,65)),F(0))
            self.assertLessEqual(finite,telescope)
            self.assertEqual(telescope,F(1,N)-F(1,64))


if __name__=='__main__':
    unittest.main(verbosity=2)
