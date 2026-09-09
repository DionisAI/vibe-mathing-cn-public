#!/usr/bin/env python3
"""Exact finite regression tests. This script does not compile Lean or call FLINT."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import re
import unittest
from hht_relative_math import (ldl_polynomials, imag_divided, annihilator,
                               evaluate, decision, dimension, cell_may_have_negative_loss)


def cmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


class RelativeTests(unittest.TestCase):
    def test_ldl_polynomial_orthogonality(self):
        """Check B A B^T=D exactly in each dimension 1..7."""
        for d in range(1,8):
            nodes=[F(1,i+1) for i in range(d+1)]
            A=[[sum(x**(i+j+1) for x in nodes) for j in range(d)] for i in range(d)]
            B,D=ldl_polynomials(A)
            for i,j in product(range(d),repeat=2):
                value=sum(B[i][r]*A[r][s]*B[j][s] for r,s in product(range(d),repeat=2))
                self.assertEqual(value, D[i] if i==j else 0)

    def test_inverse_kernel_agrees_with_squares(self):
        """A^-1=B^T D^-1 B and the orthogonal-polynomial kernel give identical values."""
        A=[[F(3,2),F(5,4)],[F(5,4),F(9,8)]]
        B,D=ldl_polynomials(A)
        inv=[[sum(B[k][i]*B[k][j]/D[k] for k in range(2)) for j in range(2)] for i in range(2)]
        for x,y in product((F(-1),F(0),F(2,5)),repeat=2):
            v=[x,y]
            lhs=sum(v[i]*inv[i][j]*v[j] for i,j in product(range(2),repeat=2))
            rhs=sum(sum(B[k][j]*v[j] for j in range(2))**2/D[k] for k in range(2))
            self.assertEqual(lhs,rhs)

    def test_divided_imaginary_identity(self):
        """Independent rational complex Horner route, including y=0 and signed y."""
        for d in range(1,9):
            poly=[F((-1)**j*(j+1),j+2) for j in range(d)]
            for x,y in product((F(0),F(1,5),F(-2,3)),repeat=2):
                val=(F(0),F(0))
                for c in reversed(poly):
                    r,i=cmul(val,(x,y));val=(r+c,i)
                self.assertEqual(y*imag_divided(poly,x,y*y),val[1])

    def test_zero_imaginary_is_derivative(self):
        """At y=0 the divided polynomial equals p'(x)."""
        p=[F(1),F(-4),F(3),F(7),F(-2)]
        for x in (F(0),F(1,5),F(3,2)):
            self.assertEqual(imag_divided(p,x,F(0)),sum(j*p[j]*x**(j-1) for j in range(1,len(p))))

    def test_point_square_identity(self):
        """The negative rank-one part is not the absolute value of the full form."""
        for x,y,P,Q in product((F(1,3),F(2)),repeat=4):
            form=x*(P*P-Q*Q)-2*y*P*Q
            self.assertEqual(x*form+(x*x+y*y)*Q*Q,(x*P-y*Q)**2)
            self.assertGreaterEqual(form,-(x*x+y*y)/x*Q*Q)

    def test_cauchy_relative_bound(self):
        """Check the relative-energy inequality on bounded exact vectors."""
        for d in range(1,9):
            a=[F((-1)**j,j+1) for j in range(d)]
            s=[F(j+1,j+2) for j in range(d)]
            self.assertLessEqual(sum(x*y for x,y in zip(a,s))**2,
                                 sum(x*x for x in a)*sum(y*y for y in s))

    def test_annihilator_is_nonzero(self):
        """Explicit polynomial witnesses certify the fixed-prefix obstruction for 1..9 nodes."""
        for n in range(1,10):
            nodes=[F(1,j+2) for j in range(n)]
            p=annihilator(nodes)
            self.assertEqual(len(p),n+1)
            self.assertEqual(p[-1],1)
            self.assertNotEqual(p[0],0)
            self.assertTrue(all(evaluate(p,u)==0 for u in nodes))
            self.assertEqual(sum(u*evaluate(p,u)**2 for u in nodes),0)

    def test_repeated_nodes_still_annihilated(self):
        """Multiplicity cannot remove the exhibited null direction."""
        p=annihilator([F(1),F(1),F(1,2)])
        self.assertEqual(evaluate(p,F(1)),0)
        self.assertEqual(evaluate(p,F(1,2)),0)

    def test_indefinite_and_singular_rejected(self):
        """Positive determinant alone cannot bypass a nonpositive pivot."""
        for A in ([[F(-1),F(0)],[F(0),F(-1)]],[[F(1),F(1)],[F(1),F(1)]]):
            with self.assertRaises(ArithmeticError): ldl_polynomials(A)

    def test_bad_shapes_and_asymmetry(self):
        """No arbitrary nonsymmetric matrix is labeled a positive Gram matrix."""
        for A in ([],[[F(1),F(2)]],[[F(1),F(0)],[F(1),F(1)]]):
            with self.assertRaises(ValueError): ldl_polynomials(A)
        for d in (0,11,True,F(2),2.0):
            with self.assertRaises(ValueError): dimension(d)

    def test_budget_equality_does_not_pass(self):
        """A large sufficient bound does not refute the target matrix."""
        self.assertEqual(decision(F(1)), 'inconclusive')
        self.assertEqual(decision(F(100)), 'inconclusive')
        self.assertEqual(decision(F(999,1000)), 'positive_under_documented_analytic_inputs')
        for bad in (F(-1),True,0.5):
            with self.assertRaises(ValueError): decision(bad)

    def test_singleton_reflection_logic(self):
        """A complete singleton cell cannot contain a non-fixed reflection pair."""
        for count,possible in ((0,False),(1,False),(2,True),(3,True)):
            self.assertEqual(cell_may_have_negative_loss(count),possible)
        for bad in (-1,True,F(1),1.0,1000001):
            with self.assertRaises(ValueError): cell_may_have_negative_loss(bad)
        for b in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
            self.assertEqual(len({b,1-b})==1,b==F(1,2))

    def test_cell_geometry_majorants(self):
        """Exact rational samples test strip enclosures and the scaled loss factor."""
        S=F(200)
        for lo in (F(50),F(53),F(100),F(255)):
            hi=lo+F(1,64)
            Xlo=S*(hi*hi-F(1,4))/(hi*hi+F(1,4))**2
            Xhi=S/(lo*lo)
            Y2hi=S*S/lo**6
            factor=S*S/(lo**8*(1-F(1,4)/(lo*lo)))
            for g in (lo,(lo+hi)/2,hi):
                for delta in (F(-1,2),F(-1,4),F(0),F(1,4),F(1,2)):
                    x=(g*g-delta*delta)/(g*g+delta*delta)**2
                    y=2*g*delta/(g*g+delta*delta)**2
                    self.assertLessEqual(Xlo,S*x)
                    self.assertLessEqual(S*x,Xhi)
                    self.assertLessEqual((S*y)**2,Y2hi)
                    self.assertLessEqual((x*x+y*y)/x*(S*y)**2,factor)

    def test_source_audits_cover_all_theorems(self):
        """Source bookkeeping only, never a substitute for actual kernel execution."""
        src=(Path(__file__).resolve().parents[1]/'fixtures/lean-proof/HHTRelative.lean').read_text()
        names=re.findall(r'^theorem\s+(\w+)',src,re.M)
        prints=re.findall(r'^#print axioms HHT006\.(\w+)',src,re.M)
        self.assertEqual(names,prints)
        self.assertGreaterEqual(len(names),8)
        self.assertIsNone(re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b',src))


if __name__=='__main__': unittest.main(verbosity=2)
