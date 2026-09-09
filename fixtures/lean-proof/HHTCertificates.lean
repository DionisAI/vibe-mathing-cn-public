import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
HHT-004 algebraic certificate slices.
The zeta counting theorem, root isolation, infinite sums and canonical product
are deliberately NOT asserted here. See HHT_LEAN.md for the exact scope.
All theorem dependencies are printed below for inspection by the runner.
-/
namespace HHT004

def lambdaRe (g d : ℝ) : ℝ := g ^ 2 - d ^ 2

def lambdaIm (g d : ℝ) : ℝ := -2 * g * d

/-- Real-coordinate identity for lambda=-(d+i*g)^2. -/
theorem lambda_norm_sq (g d : ℝ) :
    (lambdaRe g d) ^ 2 + (lambdaIm g d) ^ 2 = (g ^ 2 + d ^ 2) ^ 2 := by
  unfold lambdaRe lambdaIm
  ring

/-- Positive height excludes the spurious g=0 branch. -/
theorem lambda_im_zero_iff (g d : ℝ) (hg : 0 < g) :
    lambdaIm g d = 0 ↔ d = 0 := by
  unfold lambdaIm
  constructor
  · intro h
    rcases mul_eq_zero.mp h with hleft | hright
    · have hg0 : g ≠ 0 := ne_of_gt hg
      rcases mul_eq_zero.mp hleft with htwo | hzero
      · norm_num at htwo
      · exact (hg0 hzero).elim
    · exact hright
  · rintro rfl
    ring

/-- Strip information alone gives positive real part at height at least one. -/
theorem lambda_re_positive (g d : ℝ) (hg : 1 ≤ g) (hd : d ^ 2 ≤ 1 / 4) :
    0 < lambdaRe g d := by
  unfold lambdaRe
  nlinarith [sq_nonneg (g - 1)]

/-- Completion of the square; ordinary complex squaring is not a modulus. -/
theorem unshifted_square_identity (x y P Q : ℝ) :
    x * (x * (P ^ 2 - Q ^ 2) - 2 * y * P * Q) +
        (x ^ 2 + y ^ 2) * Q ^ 2 = (x * P - y * Q) ^ 2 := by
  ring

/-- A one-sided lower bound, NOT an upper bound on absolute magnitude. -/
theorem unshifted_block_lower (x y P Q : ℝ) (hx : 0 < x) :
    -((x ^ 2 + y ^ 2) / x) * Q ^ 2 ≤
      x * (P ^ 2 - Q ^ 2) - 2 * y * P * Q := by
  have hidentity :
      x * (x * (P ^ 2 - Q ^ 2) - 2 * y * P * Q +
          ((x ^ 2 + y ^ 2) / x) * Q ^ 2) = (x * P - y * Q) ^ 2 := by
    field_simp [ne_of_gt hx] <;> ring
  have hnonneg : 0 ≤ x * (x * (P ^ 2 - Q ^ 2) - 2 * y * P * Q +
      ((x ^ 2 + y ^ 2) / x) * Q ^ 2) := by
    rw [hidentity]
    exact sq_nonneg _
  have hrest := nonneg_of_mul_nonneg_right hnonneg hx
  linarith

/-- Substitute p(u)=a+b*u; no condition about zeta zeros is smuggled in. -/
theorem linear_polynomial_block_lower (x y a b : ℝ) (hx : 0 < x) :
    -((x ^ 2 + y ^ 2) / x) * (b * y) ^ 2 ≤
      x * ((a + b * x) ^ 2 - (b * y) ^ 2) -
        2 * y * (a + b * x) * (b * y) := by
  exact unshifted_block_lower x y (a + b * x) (b * y) hx

/-- Finite/total decomposition and both error bounds remain explicit hypotheses. -/
theorem prefix_tail_negative_transfer (total prefix tail estimate err bound : ℝ)
    (hdecomp : total = prefix + tail)
    (hprefix : |prefix - estimate| ≤ err)
    (htail : tail ≤ bound)
    (hmargin : estimate + err + bound < 0) : total < 0 := by
  have hupper := (abs_le.mp hprefix).2
  linarith

/-- Exact arithmetic from HHT-003, separate from its infinite-tail proof. -/
theorem synthetic_negative_margin :
    (-44 / 3125 : ℚ) + 1 / 100 = -51 / 12500 := by
  norm_num

/-- Formal certificate transfer for the synthetic example, conditional on its tail bound. -/
theorem conditional_synthetic_negative (total tail : ℝ)
    (hdecomp : total = -44 / 3125 + tail) (htail : tail ≤ 1 / 100) :
    total < 0 := by
  linarith

/-- Two positive-node moments have this Schur-complement numerator. -/
theorem two_node_schur_identity (u v : ℝ) :
    (u + v) * (u ^ 3 + v ^ 3) - (u ^ 2 + v ^ 2) ^ 2 =
      u * v * (u - v) ^ 2 := by
  ring

/-- The rational HHT-004 comparison has a strictly positive exact margin. -/
theorem h2_margin_arithmetic :
    (64 / 10838953125 : ℚ) - 29 / 4784677734375 =
      4035853 / 684208916015625 := by
  norm_num

/-- A conditional real inequality, not a formalization of root-data completeness. -/
theorem conditional_h2_margin_positive (schur loss : ℝ)
    (hschur : 64 / 10838953125 ≤ schur)
    (hloss : loss ≤ 29 / 4784677734375) : 0 < schur - loss := by
  linarith

end HHT004

#print axioms HHT004.lambda_norm_sq
#print axioms HHT004.lambda_im_zero_iff
#print axioms HHT004.lambda_re_positive
#print axioms HHT004.unshifted_square_identity
#print axioms HHT004.unshifted_block_lower
#print axioms HHT004.linear_polynomial_block_lower
#print axioms HHT004.prefix_tail_negative_transfer
#print axioms HHT004.synthetic_negative_margin
#print axioms HHT004.conditional_synthetic_negative
#print axioms HHT004.two_node_schur_identity
#print axioms HHT004.h2_margin_arithmetic
#print axioms HHT004.conditional_h2_margin_positive
