#!/usr/bin/env python3
"""Exact regressions for the proposed head/nullspace bridge and its obstruction."""
from fractions import Fraction as F
from itertools import product
import unittest
import hht_deflation as M

class DeflationTests(unittest.TestCase):
    def test_annihilator_values_and_monic(self):
        for n in range(1,10):
            nodes=[F(1,j+2) for j in range(n)];A=M.annihilator(nodes)
            self.assertEqual(A[-1],1)
            self.assertEqual(len(A),n+1)
            for x in nodes:self.assertEqual(M.ev(A,x),0)

    def test_polynomial_division_grid(self):
        for xs in product((-2,0,3),repeat=4):
            p=list(map(F,xs));A=M.annihilator([F(1,2),F(1,3)])
            r,q=M.split_monic(p,A)
            self.assertEqual(M.add(r,M.mul(A,q)),M.poly(p))
            self.assertLess(len(r),len(A))

    def test_nullspace_remainder_is_zero(self):
        A=M.annihilator([F(1),F(1,2)])
        for q in ([1],[1,-3,2],[0,2,-4,1]):
            r,s=M.split_monic(M.mul(A,q),A)
            self.assertEqual(r,[0]);self.assertEqual(s,M.poly(q))

    def test_prefix_form_ignores_quotient(self):
        nodes=[F(1),F(1,2),F(1,3)];A=M.annihilator(nodes)
        p=[2,-3,7,1,-2,5];r,q=M.split_monic(p,A)
        for k in range(4):
            left=sum(x**(k+1)*M.ev(p,x)**2 for x in nodes)
            right=sum(x**(k+1)*M.ev(r,x)**2 for x in nodes)
            self.assertEqual(left,right)

    def test_deflated_moment_bridge(self):
        mu=[M.signed_moment(n) for n in range(30)]
        for nodes in ([F(1)],[F(1),F(1,2)]):
            A=M.annihilator(nodes);nu=M.deflated_moments(mu,A,12)
            for q in ([1,-2],[2,3,-1],[0,1,-1]):
                for k in range(3):
                    self.assertEqual(M.bilinear(nu,q,q,k),M.bilinear(mu,M.mul(A,q),M.mul(A,q),k))

    def test_deflated_moments_independent_atomic_route(self):
        A=M.annihilator([F(1),F(1,2)]);mu=[M.signed_moment(n) for n in range(20)]
        atoms=[(F(1),F(1)),(F(1,2),F(1)),(F(1,4),-F(1,2))]
        for n,v in enumerate(M.deflated_moments(mu,A,8)):
            direct=sum(w*x**(n+1)*M.ev(A,x)**2 for x,w in atoms)
            self.assertEqual(v,direct);self.assertLess(v,0)

    def test_logconvexity_not_inherited(self):
        mu=[M.signed_moment(n) for n in range(36)]
        nu=M.deflated_moments(mu,[-1,1],30)
        for n in range(28):
            self.assertGreater(mu[n]*mu[n+2]-mu[n+1]**2,0)
            self.assertGreater(nu[n],0)
            self.assertLess(nu[n]*nu[n+2]-nu[n+1]**2,0)
        self.assertEqual(nu[:3],[F(7,128),F(23,512),F(55,2048)])

    def test_root_barrier_grid(self):
        count=0
        for x in (F(1,3),F(1,2),F(3,4)):
            for cs in product((-2,-1,0,1,2),repeat=3):
                if not any(cs):continue
                p=M.mul([-x,1],list(cs))
                rec=M.root_barrier(p,x,F(1,4),F(1))
                self.assertLessEqual(F(rec['lower_multiplier']),0);count+=1
        self.assertEqual(count,372)

    def test_111_anchor_obstruction(self):
        A=M.annihilator([F(1,j*j) for j in range(15,126)])
        rec=M.root_barrier(A,F(1,225),F(1,625),F(1,196))
        self.assertEqual(rec['sign_changes'],111)
        self.assertLess(F(rec['lower_multiplier']),0)
        self.assertEqual(rec['status'],'inconclusive')

    def test_sign_changes_after_multiplication(self):
        for n in range(1,6):
            A=M.annihilator([F(1,j+1) for j in range(n)])
            for cs in product((-2,0,1),repeat=3):
                if not any(cs):continue
                p=M.mul(A,list(cs));signs=[1 if x>0 else -1 for x in p if x]
                self.assertGreaterEqual(sum(a!=b for a,b in zip(signs,signs[1:])),n)

    def test_root_outside_interval_is_not_barrier(self):
        with self.assertRaises(ValueError):M.root_barrier([-2,1],F(2),F(1,4),F(1))

    def test_rootless_polynomial_can_have_positive_balance(self):
        from hht_balance import classify_balance
        rec=classify_balance([(0,F(1)),(1,-F(1,2))],F(1,4),F(1))
        self.assertGreater(F(rec['lower_multiplier']),0)

    def test_schur_positive_blocks_can_fail(self):
        mu=[M.signed_moment(n) for n in range(8)]
        C,E,D=M.deflation_blocks(mu,[-F(1,4),1],2);S=M.schur(C,E,D)
        self.assertEqual(C,[[F(11,8)]])
        self.assertEqual(E,[[F(7,8),F(13,16)]])
        self.assertEqual(D,[[F(19,32),F(37,64)],[F(37,64),F(73,128)]])
        M.ldl(C);M.ldl(D)
        self.assertEqual(S,[[F(13,352),F(43,704)],[F(43,704),F(127,1408)]])
        self.assertEqual(S[0][0]*S[1][1]-S[0][1]**2,-F(9,22528))
        with self.assertRaises(ArithmeticError):M.ldl(S)

    def test_schur_square_completion_grid(self):
        C=[[F(2),F(1)],[F(1),F(3)]];E=[[F(1),F(2)],[F(-1),F(1)]]
        D=[[F(5),F(1)],[F(1),F(4)]];S=M.schur(C,E,D);W=M.solve_spd(C,E)
        dot=lambda x,A,y:sum(x[i]*A[i][j]*y[j] for i in range(len(x)) for j in range(len(y)))
        for r0,r1,q0,q1 in product((-2,0,3),repeat=4):
            r=[F(r0),F(r1)];q=[F(q0),F(q1)]
            z=[r[i]+sum(W[i][j]*q[j] for j in range(2)) for i in range(2)]
            full=dot(r,C,r)+2*dot(r,E,q)+dot(q,D,q)
            self.assertEqual(full,dot(z,C,z)+dot(q,S,q))

    def test_basis_gram_matches_direct_quadratic(self):
        mu=[M.signed_moment(n) for n in range(16)];A=M.annihilator([F(1),F(1,2)])
        C,E,D=M.deflation_blocks(mu,A,2)
        r=[F(2),F(-1)];q=[F(3),F(-4)];p=M.add(r,M.mul(A,q))
        val=sum(r[i]*C[i][j]*r[j] for i in range(2) for j in range(2))
        val+=2*sum(r[i]*E[i][j]*q[j] for i in range(2) for j in range(2))
        val+=sum(q[i]*D[i][j]*q[j] for i in range(2) for j in range(2))
        self.assertEqual(val,M.bilinear(mu,p,p))

    def test_schur_determinant_independent_of_monic_chart(self):
        mu=[M.signed_moment(n) for n in range(12)]
        H=[[mu[i+j] for j in range(4)] for i in range(4)]
        # Two positive and one negative atom make rank three; use size three too.
        for d in (3,4):
            H=[[mu[i+j] for j in range(d)] for i in range(d)]
            for A in ([0,0,1],[1,-3,1],[F(1,2),-F(3,2),1]):
                C,E,D=M.deflation_blocks(mu,A,d-2)
                self.assertEqual(M.determinant(C)*M.determinant(M.schur(C,E,D)),M.determinant(H))

    def test_determinant_pivoting_and_singularity(self):
        self.assertEqual(M.determinant([[0,1],[1,0]]),-1)
        self.assertEqual(M.determinant([[1,2],[2,4]]),0)
        with self.assertRaises(ValueError):M.determinant([[1,2]])

    def test_spd_solve_is_exact(self):
        C=[[2,1],[1,3]];E=[[1,2],[-1,1]]
        self.assertEqual(M.matmul(C,M.solve_spd(C,E)),M.matrix(E))

    def test_rank_one_no_positive_uniform_margin(self):
        p=[-F(1,2),1]
        for denominator in (10,100,1000):
            eps=F(1,denominator);x=F(1,2);y=F(1,3)
            mu=[x**(n+1)+eps*y**(n+1) for n in range(4)]
            self.assertGreater(mu[0]*mu[2]-mu[1]**2,0)
            self.assertEqual(M.bilinear(mu,p,p),eps*y*M.ev(p,y)**2)
            self.assertLess(M.bilinear(mu,p,p)/mu[0],eps)

    def test_boundary_is_not_positive(self):
        rec=M.root_barrier([-F(1,2),1],F(1,2),F(1,4),F(1))
        self.assertEqual(F(rec['lower_multiplier']),0)

    def test_report_flags(self):
        r=M.report()
        self.assertFalse(r['rh_proved']);self.assertFalse(r['new_actual_xi_numerical_claim'])
        self.assertFalse(r['rational_111_anchor_example']['is_actual_xi_root_data'])

    def test_bad_rationals_and_nodes(self):
        for x in (0.5,True,'1',F(1,1<<32769)):
            with self.assertRaises(ValueError):M.rat(x)
        for nodes in ([],[0],[1,1],[-1],[1.0]):
            with self.assertRaises(ValueError):M.annihilator(nodes)

    def test_bad_polynomials_and_missing_moments(self):
        for p in ([],[1]*258,[True],['1']):
            with self.assertRaises(ValueError):M.poly(p)
        for A in ([0],[1],[1,2]):
            with self.assertRaises(ValueError):M.split_monic([1,2,3],A)
        with self.assertRaises(ValueError):M.bilinear([1,2],[1,2],[1,2])
        with self.assertRaises(ValueError):M.bilinear([1,2],[1],[1],True)

    def test_bad_matrix_and_nonpositive_head(self):
        for C in ([],[[1,2]],[[1,2],[0,1]],[[0]],[[True]]):
            with self.assertRaises((ValueError,ArithmeticError)):M.ldl(C)
        with self.assertRaises(ValueError):M.schur([[1]],[[1,2]],[[1]])
        with self.assertRaises(ArithmeticError):M.schur([[-1]],[[0]],[[1]])

if __name__=='__main__':unittest.main(verbosity=2)
