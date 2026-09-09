import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
HHT-006: a dimension-parametric relative-loss certificate in prefix-normalized
coordinates. Summability and the kernel budget are explicit premises. There is
no assertion that zeta satisfies the budget in every dimension.
-/
namespace HHT006
noncomputable section
open scoped BigOperators

def energy {d : ℕ} (a : Fin d → ℝ) : ℝ := ∑ i, (a i) ^ 2

def pairing {d : ℕ} (a b : Fin d → ℝ) : ℝ := ∑ i, a i * b i

def pointForm (x y P Q : ℝ) : ℝ := x * (P ^ 2 - Q ^ 2) - 2 * y * P * Q

def lossWeight (x y : ℝ) : ℝ := (x ^ 2 + y ^ 2) / x

/-- The reference energy is a sum of real squares. -/
theorem energy_nonneg {d : ℕ} (a : Fin d → ℝ) : 0 ≤ energy a := by
  exact Finset.sum_nonneg (fun i _ => sq_nonneg (a i))

/-- A nonzero coefficient vector has strictly positive normalized energy. -/
theorem energy_pos {d : ℕ} (a : Fin d → ℝ) (ha : ∃ i, a i ≠ 0) :
    0 < energy a := by
  obtain ⟨i, hi⟩ := ha
  exact Finset.sum_pos' (fun j _ => sq_nonneg (a j))
    ⟨i, Finset.mem_univ i, sq_pos_of_ne_zero hi⟩

/-- Finite-dimensional Cauchy-Schwarz, with no fixed numerical dimension. -/
theorem pairing_square_le {d : ℕ} (a b : Fin d → ℝ) :
    (pairing a b) ^ 2 ≤ energy a * energy b := by
  exact Finset.sum_mul_sq_le_sq_mul_sq Finset.univ a b

/-- Exact positive-square minus rank-one-loss identity after clearing x. -/
theorem completed_square (x y P Q : ℝ) :
    x * pointForm x y P Q + (x ^ 2 + y ^ 2) * Q ^ 2 =
      (x * P - y * Q) ^ 2 := by
  unfold pointForm
  ring

/-- One-sided loss bound. It is not a bound on absolute tail magnitude. -/
theorem point_lower (x y P Q : ℝ) (hx : 0 < x) :
    -(lossWeight x y) * Q ^ 2 ≤ pointForm x y P Q := by
  have hident : x * (pointForm x y P Q + lossWeight x y * Q ^ 2) =
      (x * P - y * Q) ^ 2 := by
    unfold pointForm lossWeight
    field_simp [ne_of_gt hx]
    ring
  have hh : 0 ≤ x * (pointForm x y P Q + lossWeight x y * Q ^ 2) := by
    rw [hident]
    exact sq_nonneg _
  have hh' := nonneg_of_mul_nonneg_right hh hx
  linarith

/-- Each tail node is controlled relative to the prefix energy, not a tiny eigenvalue. -/
theorem point_relative_lower {d : ℕ} (a r s : Fin d → ℝ) (x y : ℝ)
    (hx : 0 < x) :
    -(lossWeight x y * energy s) * energy a ≤
      pointForm x y (pairing a r) (pairing a s) := by
  have hw : 0 ≤ lossWeight x y := by
    exact div_nonneg (add_nonneg (sq_nonneg x) (sq_nonneg y)) hx.le
  have hc := mul_le_mul_of_nonneg_left (pairing_square_le a s) hw
  have hl := point_lower x y (pairing a r) (pairing a s) hx
  nlinarith

/-- Transfer the relative bound to a genuine infinite sum with explicit convergence. -/
theorem infinite_relative_lower {d : ℕ} (a : Fin d → ℝ)
    (x y : ℕ → ℝ) (r s : ℕ → Fin d → ℝ)
    (hx : ∀ n, 0 < x n)
    (hp : Summable (fun n => pointForm (x n) (y n) (pairing a (r n)) (pairing a (s n))))
    (hk : Summable (fun n => lossWeight (x n) (y n) * energy (s n))) :
    -(∑' n, lossWeight (x n) (y n) * energy (s n)) * energy a ≤
      ∑' n, pointForm (x n) (y n) (pairing a (r n)) (pairing a (s n)) := by
  have h := hasSum_le
    (fun n => point_relative_lower a (r n) (s n) (x n) (y n) (hx n))
    ((hk.hasSum.neg).mul_right (energy a)) hp.hasSum
  exact h

/-- A budget below one proves positivity for every nonzero vector in any finite dimension. -/
theorem full_relative_positive {d : ℕ} (a : Fin d → ℝ)
    (x y : ℕ → ℝ) (r s : ℕ → Fin d → ℝ) (pref kappa : ℝ)
    (ha : ∃ i, a i ≠ 0) (hx : ∀ n, 0 < x n)
    (hp : Summable (fun n => pointForm (x n) (y n) (pairing a (r n)) (pairing a (s n))))
    (hk : Summable (fun n => lossWeight (x n) (y n) * energy (s n)))
    (hprefix : energy a ≤ pref)
    (hbudget : (∑' n, lossWeight (x n) (y n) * energy (s n)) ≤ kappa)
    (hsmall : kappa < 1) :
    0 < pref + ∑' n, pointForm (x n) (y n) (pairing a (r n)) (pairing a (s n)) := by
  have he := energy_pos a ha
  have htail := infinite_relative_lower a x y r s hx hp hk
  have hb := mul_le_mul_of_nonneg_right hbudget he.le
  have hstrict : 0 < (1 - kappa) * energy a := mul_pos (sub_pos.mpr hsmall) he
  nlinarith

def annihilator {n : ℕ} (nodes : Fin n → ℝ) (t : ℝ) : ℝ :=
  ∏ i, (t - nodes i)

def prefixEnergy {n : ℕ} (nodes weights : Fin n → ℝ) (p : ℝ → ℝ) : ℝ :=
  ∑ i, weights i * (p (nodes i)) ^ 2

/-- The explicitly given degree-n product vanishes at every one of n prefix nodes. -/
theorem annihilator_at_node {n : ℕ} (nodes : Fin n → ℝ) (i : Fin n) :
    annihilator nodes (nodes i) = 0 := by
  unfold annihilator
  apply Finset.prod_eq_zero (Finset.mem_univ i)
  simp

/-- Positive prefix nodes imply this finite product is not the zero function. -/
theorem annihilator_at_zero_ne {n : ℕ} (nodes : Fin n → ℝ)
    (hn : ∀ i, 0 < nodes i) : annihilator nodes 0 ≠ 0 := by
  unfold annihilator
  apply Finset.prod_ne_zero_iff.mpr
  intro i _
  exact sub_ne_zero.mpr (ne_of_lt (hn i))

/-- No prefix energy survives in the annihilating polynomial direction. -/
theorem prefix_annihilator_zero {n : ℕ} (nodes weights : Fin n → ℝ) :
    prefixEnergy nodes weights (annihilator nodes) = 0 := by
  simp [prefixEnergy, annihilator_at_node]

/-- A fixed finite prefix cannot dominate even this positive penalty in every polynomial direction. -/
theorem fixed_prefix_obstruction {n : ℕ} (nodes weights : Fin n → ℝ) (eps : ℝ)
    (hn : ∀ i, 0 < nodes i) (heps : 0 < eps) :
    prefixEnergy nodes weights (annihilator nodes) < eps * (annihilator nodes 0) ^ 2 := by
  rw [prefix_annihilator_zero]
  exact mul_pos heps (sq_pos_of_ne_zero (annihilator_at_zero_ne nodes hn))

end HHT006

#print axioms HHT006.energy_nonneg
#print axioms HHT006.energy_pos
#print axioms HHT006.pairing_square_le
#print axioms HHT006.completed_square
#print axioms HHT006.point_lower
#print axioms HHT006.point_relative_lower
#print axioms HHT006.infinite_relative_lower
#print axioms HHT006.full_relative_positive
#print axioms HHT006.annihilator_at_node
#print axioms HHT006.annihilator_at_zero_ne
#print axioms HHT006.prefix_annihilator_zero
#print axioms HHT006.fixed_prefix_obstruction
