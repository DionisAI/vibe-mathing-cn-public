#!/usr/bin/env python3
"""Exact regression checks for HHT-004, not a zero isolation or Lean verifier."""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fixtures'))
import xi_strip as M


class XiStripTests(unittest.TestCase):
    def test_mapping_identity_grid(self):
        """Check the squared-modulus identity at 75 rational strip points."""
        for beta, gamma in product((F(0), F(1,4), F(1,2), F(3,4), F(1)), range(1,16)):
            x,y=M.lambda_coordinates(beta,gamma)
            self.assertEqual(x*x+y*y,(F(gamma)**2+(beta-F(1,2))**2)**2)

    def test_reflection_preserves_real_flips_imaginary(self):
        """The upper-strip reflection, not lower-half-plane duplication, is used."""
        for beta in (F(0),F(1,3),F(1,2)):
            x,y=M.lambda_coordinates(beta,14)
            self.assertEqual(M.lambda_coordinates(1-beta,14),(x,-y))

    def test_line_equivalence(self):
        """Positive gamma makes a real lambda equivalent to beta=1/2."""
        for beta in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
            self.assertEqual(M.lambda_coordinates(beta,14)[1]==0,beta==F(1,2))

    def test_height_is_not_modulus(self):
        """A height-50 prefix may include a node with |lambda|>2500."""
        a,b=M.lambda_coordinates(F(3,4),50)
        self.assertGreater(a*a+b*b,F(2500)**2)
        boxes=[M.RootBox(F(1,4),F(1,4),50,50),M.RootBox(F(3,4),F(3,4),50,50)]
        self.assertEqual(M.prefix_structure(boxes,50)['cutoff_kind'],'height')

    def test_log_enclosures_against_high_precision_sanity(self):
        """Decimal ln is a sanity comparison; the analytic enclosure proof is in the note."""
        with localcontext() as ctx:
            ctx.prec=120
            for value in (1,2,3,50,100,1024,F(71,3),10**20):
                z=F(value); interval=M.log_interval(z)
                actual=(Decimal(z.numerator)/Decimal(z.denominator)).ln()
                low=Decimal(interval.lo.numerator)/Decimal(interval.lo.denominator)
                high=Decimal(interval.hi.numerator)/Decimal(interval.hi.denominator)
                self.assertLessEqual(low,actual); self.assertLessEqual(actual,high)

    def test_log_nested_and_four_bound(self):
        """More positive atanh terms tighten the rational upper and lower bounds."""
        previous=M.log_interval(50,1)
        for n in (2,4,8,16):
            current=M.log_interval(50,n)
            self.assertLessEqual(previous.lo,current.lo)
            self.assertLessEqual(current.hi,previous.hi)
            previous=current
        self.assertLess(previous.hi,4)

    def test_power_formula_at_50(self):
        """Verify the integral expression's finite exact parameter specialization."""
        L=M.log_interval(50).hi
        for q in range(2,17):
            self.assertEqual(M.height_power_bound(50,q),q*F(50)**(1-q)*(L/(q-1)+F(1,(q-1)**2)))

    def test_power_bound_decreases_with_height(self):
        """Check representative monotone regimes without claiming universal proof by sampling."""
        for q in range(2,17):
            self.assertGreater(M.height_power_bound(50,q),M.height_power_bound(100,q))

    def test_completed_square_identity(self):
        """Check 54 exact square completions used in the analytic proof."""
        for x,y,P,Q in product((F(1,5),F(1),F(2)),(F(-2),F(0),F(3)),(F(-1),F(2)),(F(-3),F(0),F(1))):
            value=x*(P*P-Q*Q)-2*y*P*Q
            self.assertEqual(x*value+(x*x+y*y)*Q*Q,(x*P-y*Q)**2)
            self.assertGreaterEqual(value,-(x*x+y*y)*Q*Q/x)

    def test_point_negative_bound_for_polynomials(self):
        """Check derivative-weighted lower bounds on 48 synthetic rational strip cases."""
        for beta,gamma,p in product((F(0),F(1,4),F(1,2),F(1)),(50,51,100),
                ((0,1),(1,2,3),(-1,3,-2,1),(F(2,5),-F(7,5),1))):
            v=M.point_unshifted_term(beta,gamma,p)
            derivative=sum((i*abs(F(c))*F(gamma)**(-2*(i-1)) for i,c in enumerate(p) if i),F(0))
            bound=F(gamma)**(-8)*derivative**2/(1-F(1,4*50**2))
            self.assertGreaterEqual(v,-bound)

    def test_constant_has_no_negative_tail(self):
        """A zero lower-loss bound is NOT an upper bound on absolute tail size."""
        self.assertEqual(M.negative_quadratic_tail([1],50),0)
        self.assertGreater(M.absolute_quadratic_tail([1],0,50),0)
        self.assertGreater(M.point_unshifted_term(F(1,4),51,[1]),0)

    def test_slope_and_matrix_bounds_coincide(self):
        """In dimension two the loss is only on the slope coefficient."""
        self.assertEqual(M.negative_quadratic_tail([0,1],50),M.negative_matrix_tail(2,50))
        self.assertEqual(M.negative_quadratic_tail([123,2],50),4*M.negative_matrix_tail(2,50))
        self.assertEqual(M.negative_matrix_tail(1,50),0)

    def test_negative_is_tighter_than_absolute_in_example(self):
        """Compare bounds for one fixed p; these bounds have different logical directions."""
        self.assertLess(1000*M.negative_quadratic_tail([0,1],50),M.absolute_quadratic_tail([0,1],0,50))

    def test_known_coarse_margin(self):
        """Check exact arithmetic, leaving the two root-location premises unverified."""
        value=M.coarse_h2_comparison()
        self.assertEqual(value['prefix_schur_lower'],F(64,10838953125))
        self.assertEqual(value['tail_negative_upper'],F(29,4784677734375))
        self.assertEqual(value['margin'],F(4035853,684208916015625))
        self.assertGreater(value['margin'],0)
        self.assertLess(M.negative_matrix_tail(2,50),value['tail_negative_upper'])
        self.assertEqual(value['status'],'conditional_on_unverified_zero_inputs')

    def test_interval_square_and_inverse(self):
        """Enclosures handle zero crossing, negative reciprocal and singularity."""
        self.assertEqual(M.Interval(-2,3).square(),M.Interval(0,9))
        self.assertEqual(M.Interval(-4,-2).reciprocal(),M.Interval(-F(1,2),-F(1,4)))
        with self.assertRaises(ValueError): M.Interval(-1,1).reciprocal()

    def test_degenerate_box_prefix_matches_points(self):
        """A rational fake zero example checks two independent arithmetic paths."""
        boxes=[M.RootBox(F(1,4),F(1,4),20,20),M.RootBox(F(3,4),F(3,4),20,20)]
        for p in ([1],[0,1],[1,2,3],[-1,3,-2,1]):
            enclosure=M.conditional_prefix_interval(boxes,p,50)
            value=sum((M.point_unshifted_term(b.beta_lo,b.gamma_lo,p) for b in boxes),F(0))
            self.assertEqual(enclosure,M.point(value))

    def test_nondegenerate_box_contains_samples(self):
        """Rational interval propagation encloses 36 symmetric sampled prefix values."""
        boxes=[M.RootBox(F(1,4),F(1,3),20,21),M.RootBox(F(2,3),F(3,4),20,21)]
        for p in ([1],[0,1],[1,-2,3],[-1,3,-2,1]):
            interval=M.conditional_prefix_interval(boxes,p,50)
            for beta,gamma in product((F(1,4),F(7,24),F(1,3)),(F(20),F(41,2),F(21))):
                value=M.point_unshifted_term(beta,gamma,p)+M.point_unshifted_term(1-beta,gamma,p)
                self.assertLessEqual(interval.lo,value); self.assertLessEqual(value,interval.hi)

    def test_structure_never_certifies_roots(self):
        """Even correct shape and reflected boxes cannot self-declare completeness."""
        value=M.prefix_structure([M.RootBox(F(1,2),F(1,2),14,15)],50)
        self.assertFalse(value['actual_zeros_verified']); self.assertFalse(value['completeness_verified'])

    def test_duplicate_and_overlap_rejected(self):
        """Avoid double-counting roots lying on common closed boundaries."""
        a=M.RootBox(F(1,2),F(1,2),14,15)
        for boxes in ([a,a],[a,M.RootBox(F(1,2),F(1,2),15,16)]):
            with self.assertRaises(ValueError): M.prefix_structure(boxes,50)

    def test_missing_reflection_or_multiplicity_rejected(self):
        """Off-line boxes must be paired in the upper half-plane at equal multiplicity."""
        a=M.RootBox(F(1,4),F(1,4),20,21)
        for boxes in ([a],[a,M.RootBox(F(3,4),F(3,4),20,21,2)]):
            with self.assertRaises(ValueError): M.prefix_structure(boxes,50)

    def test_cutoff_and_lower_half_rejected(self):
        """The adapter never silently drops boxes crossing the selected height."""
        with self.assertRaises(ValueError): M.RootBox(F(1,2),F(1,2),-20,-19)
        with self.assertRaises(ValueError): M.prefix_structure([M.RootBox(F(1,2),F(1,2),49,51)],50)

    def test_parameter_and_budget_rejections(self):
        """Reject ambiguous, divergent and over-budget caller inputs."""
        for bad in (True,0.5,'1',1<<129):
            with self.assertRaises(ValueError): M.rat(bad)
        for T in (0,49):
            with self.assertRaises(ValueError): M.height_power_bound(T,8)
            with self.assertRaises(ValueError): M.negative_matrix_tail(2,T)
        for q in (1,True,M.MAX_POWER+1):
            with self.assertRaises(ValueError): M.height_power_bound(50,q)
        for p in ([],[0],[1]*14):
            with self.assertRaises(ValueError): M.negative_quadratic_tail(p,50)
        with self.assertRaises(ValueError): M.log_interval(F(1,2))
        with self.assertRaises(ValueError): M.log_interval(50,33)
        with self.assertRaises(ValueError): M.negative_matrix_tail(14,50)


if __name__=='__main__': unittest.main(verbosity=2)
