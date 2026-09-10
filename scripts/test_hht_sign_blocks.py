#!/usr/bin/env python3
"""Exact finite regressions; no RH claim or infinite-kernel verification."""
from fractions import Fraction as F
from itertools import combinations
import unittest
import hht_sign_blocks as B


class BlockTests(unittest.TestCase):
    def test_zero_ignored(self):
        b,s=B.sign_blocks([(0,2),(1,0),(2,3),(4,-4),(5,0),(9,-1)])
        self.assertEqual(s,(1,-1));self.assertEqual(len(b),2)

    def test_dense_fifty_not_sparse_ten(self):
        r=B.classify_direction([(i,(-1)**(i//5)) for i in range(50)])
        self.assertEqual((r['nonzero_terms'],r['sign_changes']),(50,9))
        self.assertTrue(r['covered_if_kernel_is_strict_TP_order'])
        self.assertFalse(r['kernel_input_verified_here'])

    def test_unbounded_degree_screen(self):
        r=B.classify_direction([(0,1),(1000,2),(999999,-3),(1000000,-1)])
        self.assertEqual(r['sign_changes'],1)

    def test_more_changes_is_unknown(self):
        r=B.classify_direction([(i,(-1)**i) for i in range(11)])
        self.assertFalse(r['covered_if_kernel_is_strict_TP_order'])
        self.assertNotIn('negative',r)

    def test_all_same_sign(self):
        for s in (-1,1):
            self.assertEqual(B.classify_direction([(i,s) for i in range(128)])['sign_changes'],0)

    def test_global_negation(self):
        a=[(i,(-1)**(i//3)*(i+1)) for i in range(12)]
        self.assertEqual(B.sign_blocks(a)[0],B.sign_blocks([(i,-c) for i,c in a])[0])

    def test_empty_zero_and_nonrational(self):
        for a in ([],[(1,0)],[(1,True)],[(1,0.5)],[(1,'1')]):
            with self.assertRaises(ValueError):B.sign_blocks(a)

    def test_exponents(self):
        for a in ([(-1,1)],[(True,1)],[(1,1),(1,-1)],[(2,1),(0,1)],[(1000001,1)]):
            with self.assertRaises(ValueError):B.sign_blocks(a)

    def test_support_validation(self):
        for b in ([],[[]],[[(0,0)]],[[(0,-1)]],[[(0,1),(2,1)],[(1,1)]],[[(0,1)],[(0,1)]]):
            with self.assertRaises(ValueError):B.validate_blocks(b)

    def test_resource_limits(self):
        with self.assertRaises(ValueError):B.sign_blocks([(i,1) for i in range(129)])
        with self.assertRaises(ValueError):B.rational(1<<2049)
        with self.assertRaises(ValueError):B.validate_blocks([[(i,1)] for i in range(17)])
        b=[[(i*4+j,1) for j in range(4)] for i in range(4)]
        with self.assertRaises(ValueError):B.expanded_determinant(lambda i,j:F(1,i+j+1),b)

    def test_exact_determinant(self):
        self.assertEqual(B.determinant([]),1)
        self.assertEqual(B.determinant([[0,2],[3,4]]),-6)
        self.assertEqual(B.determinant([[1,2],[2,4]]),0)
        self.assertIsInstance(B.determinant([[1,2],[2,5]]),F)

    def test_cauchy_expansion(self):
        K=lambda i,j:F(1,i+j+1)
        for s in range(1,5):
            rows=[[(3*i,F(i+1)),(3*i+1,F(1,2))] for i in range(s)]
            cols=[[(4*i,F(2,3)),(4*i+2,F(3))] for i in range(s)]
            e=B.expanded_determinant(K,rows,cols)
            self.assertEqual(e['determinant'],B.determinant(B.compress(K,rows,cols)))
            self.assertGreater(e['minimum_selected_minor'],0)

    def test_all_compressed_minors(self):
        K=lambda i,j:F(1,i+j+1)
        blocks=[[(2*i,1),(2*i+1,2)] for i in range(4)]
        C=B.compress(K,blocks)
        for s in range(1,5):
            for a in combinations(range(4),s):
                for b in combinations(range(4),s):
                    self.assertGreater(B.determinant([[C[i][j] for j in b] for i in a]),0)

    def test_direction_reconstruction(self):
        K=lambda i,j:F(1,i+j+1)
        terms=[(i,(-1)**(i//3)*(i+1)) for i in range(12)]
        bs,ss=B.sign_blocks(terms);C=B.compress(K,bs)
        direct=B.quadratic([[K(i,j) for j,_ in terms] for i,_ in terms],[c for _,c in terms])
        self.assertEqual(B.quadratic(C,ss),direct);self.assertGreater(direct,0)

    def test_tp2_boundary(self):
        mu=[1,2,5,14,40];A=[[mu[i+j] for j in range(3)] for i in range(3)]
        for s in (1,2):
            for a in combinations(range(3),s):
                for b in combinations(range(3),s):
                    self.assertGreater(B.determinant([[A[i][j] for j in b] for i in a]),0)
        self.assertEqual(B.quadratic(A,[3,-4,1]),-1)
        self.assertEqual(B.sign_blocks([(0,3),(1,-4),(2,1)])[1],(1,-1,1))

    def test_two_ordered_blocks_positive(self):
        mu=[1,2,5,14,40];K=lambda i,j:mu[i+j]
        for a in (1,2,3):
            for b in (1,2,3):
                C=B.compress(K,[[(0,a),(1,b)],[(2,1)]])
                self.assertGreater(B.determinant(C),0)
                self.assertGreater(B.quadratic(C,[1,-1]),0)

    def test_interlacing_cannot_group_by_sign_only(self):
        with self.assertRaises(ValueError):B.compress(lambda i,j:1,[[(0,3),(2,1)],[(1,4)]])
        self.assertEqual(B.quadratic([[79,80],[80,80]],[1,-1]),-1)

    def test_index_gaps_and_shift(self):
        mu=lambda n:sum(F(x,8)**(n+1) for x in range(1,8))
        for k in (0,1,3):
            bs=[[(0,1),(2,2)],[(5,3),(9,1)],[(10,2)]]
            K=lambda i,j:mu(k+i+j)
            self.assertEqual(B.expanded_determinant(K,bs)['determinant'],B.determinant(B.compress(K,bs)))

    def test_scaling(self):
        K=lambda i,j:F(1,i+j+1);b=[[(0,1),(1,2)],[(3,3)]]
        c=B.compress(K,b);d=B.compress(K,[[(i,2*w) for i,w in block] for block in b])
        self.assertEqual(d,[[4*x for x in row] for row in c])

    def test_mixed_shape_and_approximate_kernel(self):
        b=[[(0,1)],[(2,1)]]
        with self.assertRaises(ValueError):B.compress(lambda i,j:0.5,b)
        with self.assertRaises(ValueError):B.expanded_determinant(lambda i,j:1,b,b[:1])
        with self.assertRaises(ValueError):B.quadratic([[1]],[1,2])


if __name__=='__main__':unittest.main(verbosity=2)
