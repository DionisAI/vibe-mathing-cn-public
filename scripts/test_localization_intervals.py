#!/usr/bin/env python3
"""Tests for the independent rational interval blind-spot calculation."""
from fractions import Fraction as F
from itertools import product
import unittest
from certify_localization_blindspot import Interval as I, atan_reciprocal, pi_interval, bernoulli, positive_ldl, certify


class IntervalTests(unittest.TestCase):
    def test_outward_rounding(self):
        """Every rounded interval contains both exact original endpoints."""
        for a,b in product((F(-7,3),F(-1,5),F(0),F(4,7)),repeat=2):
            lo,hi=min(a,b),max(a,b); x=I(lo,hi,64)
            self.assertLessEqual(x.lo,lo); self.assertGreaterEqual(x.hi,hi)

    def test_rational_operations(self):
        """Check all corner products and sums across signs, without floats."""
        for a,b in product((I(-2,-1,64),I(-1,2,64),I(1,3,64)),repeat=2):
            for x,y in product((a.lo,a.hi),(b.lo,b.hi)):
                for out,v in ((a+b,x+y),(a-b,x-y),(a*b,x*y)):
                    self.assertLessEqual(out.lo,v); self.assertGreaterEqual(out.hi,v)
                if not b.lo<=0<=b.hi:
                    out=a/b; self.assertLessEqual(out.lo,x/y); self.assertGreaterEqual(out.hi,x/y)

    def test_rejections(self):
        """No division across zero, float input, inverted intervals or mixed precision."""
        for args in ((0.5,1,64),(True,1,64),(2,1,64),(0,1,2048)):
            with self.assertRaises(ValueError): I(*args)
        with self.assertRaises(ArithmeticError): I(1,2,64)/I(-1,1,64)
        with self.assertRaises(ValueError): I(1,1,64)+I(1,1,128)

    def test_bernoulli(self):
        """The recurrence agrees with its known first even rational values."""
        B=bernoulli(10)
        self.assertEqual([B[n] for n in (0,1,2,4,6,8,10)],
                         [F(1),-F(1,2),F(1,6),-F(1,30),F(1,42),-F(1,30),F(5,66)])
        self.assertTrue(all(B[n]==0 for n in (3,5,7,9)))

    def test_atan_nested(self):
        """The alternating-series remainder intervals nest."""
        for q in (5,239):
            a=atan_reciprocal(q,10); b=atan_reciprocal(q,20)
            self.assertLessEqual(a[0],b[0]); self.assertLessEqual(b[1],a[1])

    def test_machin_identity_algebra(self):
        """The tangent of 4*atan(1/5)-atan(1/239) is exactly 1."""
        tan2=2*F(1,5)/(1-F(1,25)); tan4=2*tan2/(1-tan2**2)
        self.assertEqual(tan4,F(120,119))
        self.assertEqual((tan4-F(1,239))/(1+tan4*F(1,239)),1)
        p=pi_interval(256)
        self.assertGreater(p.lo,F(314159,100000)); self.assertLess(p.hi,F(314160,100000))

    def test_schur_known(self):
        """Positive Schur pivots are not inferred from determinant sign alone."""
        out=positive_ldl([[I(2,2,64),I(1,1,64)],[I(1,1,64),I(2,2,64)]])
        self.assertEqual((out[0].lo,out[1].lo),(2,F(3,2)))
        for matrix in ([[I(-1,-1,64),I(0,0,64)],[I(0,0,64),I(-1,-1,64)]],[[I(0,0,64)]],
                       [[I(1,1,64),I(1,1,64)],[I(1,1,64),I(1,1,64)]]):
            with self.assertRaises(ArithmeticError): positive_ldl(matrix)
        with self.assertRaises(ValueError): positive_ldl([[I(1,1,64),I(2,2,64)]])
        with self.assertRaises(ValueError): positive_ldl([[I(2,2,64),I(0,0,64)],[I(1,1,64),I(2,2,64)]])

    def test_full_infinite_blindspot(self):
        """Exact positive H8 and negative H108 concern the same entire infinite spectrum."""
        results=[certify(bits) for bits in (256,512)]
        for r in results:
            self.assertTrue(all(p.lo>0 for p in r['pivots']))
            self.assertEqual(r['witness']['dimension'],108)
            self.assertLess(r['witness']['full_upper'],-F(1,100))
            self.assertFalse(r['lean_kernel_checked'])
        for a,b in zip(results[0]['moments'],results[1]['moments']):
            self.assertLessEqual(max(a.lo,b.lo),min(a.hi,b.hi))


if __name__=='__main__':
    unittest.main(verbosity=2)
