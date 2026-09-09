import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Topology.Algebra.InfiniteSum.Ring
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Shift lifting in arbitrary finite dimension. The full-tail envelope and the
finite exceptional cases are explicit premises, not assertions about xi.
No finite root list is substituted for the whole infinite tail.
-/
set_option autoImplicit false
namespace HHTShifts
noncomputable section
open scoped BigOperators

def budget {d : ℕ} (c a : Fin d → ℝ) (k : ℕ) : ℝ :=
  ∑ i, c i * a i ^ k

/-- A geometric sum with nonnegative coefficients is nonnegative. -/
theorem budget_nonneg {d : ℕ} (c a : Fin d → ℝ)
    (hc : ∀ i, 0 ≤ c i) (ha : ∀ i, 0 ≤ a i) (k : ℕ) :
    0 ≤ budget c a k := by
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (hc i) (pow_nonneg (ha i) k))

/-- Contracting every ratio makes the whole budget decrease at every shift. -/
theorem budget_step_le {d : ℕ} (c a : Fin d → ℝ)
    (hc : ∀ i, 0 ≤ c i) (ha0 : ∀ i, 0 ≤ a i) (ha1 : ∀ i, a i ≤ 1) (k : ℕ) :
    budget c a (k+1) ≤ budget c a k := by
  apply Finset.sum_le_sum
  intro i _
  have h : a i ^ (k+1) ≤ a i ^ k := by
    rw [pow_succ]
    exact mul_le_of_le_one_right (pow_nonneg (ha0 i) k) (ha1 i)
  exact mul_le_mul_of_nonneg_left h (hc i)

/-- One finite threshold controls every later natural-number shift. -/
theorem budget_add_le {d : ℕ} (c a : Fin d → ℝ)
    (hc : ∀ i, 0 ≤ c i) (ha0 : ∀ i, 0 ≤ a i) (ha1 : ∀ i, a i ≤ 1)
    (K n : ℕ) : budget c a (K+n) ≤ budget c a K := by
  induction n with
  | zero => simp
  | succ n ih =>
    exact (budget_step_le c a hc ha0 ha1 (K+n)).trans ih

/-- The strict threshold remains strict for all k>=K, not just sampled shifts. -/
theorem budget_below_one_after {d : ℕ} (c a : Fin d → ℝ)
    (hc : ∀ i, 0 ≤ c i) (ha0 : ∀ i, 0 ≤ a i) (ha1 : ∀ i, a i ≤ 1)
    (K k : ℕ) (hK : K ≤ k) (hb : budget c a K < 1) : budget c a k < 1 := by
  have h := budget_add_le c a hc ha0 ha1 K (k-K)
  have heq : K + (k-K) = k := Nat.add_sub_of_le hK
  rw [heq] at h
  exact lt_of_le_of_lt h hb

/-- Real and imaginary parts of normalized interpolation satisfy Cauchy-Schwarz. -/
theorem complex_pairing_bound {d : ℕ} (v r s : Fin d → ℝ) :
    (∑ i, v i * r i)^2 + (∑ i, v i * s i)^2 ≤
      (∑ i, (v i)^2) * ((∑ i, (r i)^2) + (∑ i, (s i)^2)) := by
  have hr := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ v r
  have hs := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ v s
  nlinarith

/-- A pointwise lower envelope passes to the genuine infinite sum. -/
theorem infinite_envelope_lower (A : ℝ) (tail envelope : ℕ → ℝ)
    (ht : Summable tail) (he : Summable envelope)
    (hpoint : ∀ n, -A * envelope n ≤ tail n) :
    -A * (∑' n, envelope n) ≤ ∑' n, tail n := by
  exact hasSum_le hpoint (he.hasSum.mul_left (-A)) ht.hasSum

/-- A relative absolute-tail budget below one leaves a positive full form. -/
theorem one_shift_positive (A extra b : ℝ) (tail envelope : ℕ → ℝ)
    (hA : 0 < A) (hx : 0 ≤ extra) (hb : b < 1)
    (ht : Summable tail) (he : Summable envelope)
    (hpoint : ∀ n, -A * envelope n ≤ tail n)
    (hsum : (∑' n, envelope n) ≤ b) :
    0 < A + extra + ∑' n, tail n := by
  have hl := infinite_envelope_lower A tail envelope ht he hpoint
  have hm := mul_le_mul_of_nonneg_left hsum hA.le
  have hp : 0 < A * (1-b) := mul_pos hA (sub_pos.mpr hb)
  nlinarith

/-- Finite exceptional shifts plus one contracting bound cover all shifts and directions.
The interpolation envelope, convergence and true coefficient checks remain explicit. -/
theorem all_shifts_positive {d m : ℕ} (c a : Fin m → ℝ)
    (hc : ∀ i, 0 ≤ c i) (ha0 : ∀ i, 0 ≤ a i) (ha1 : ∀ i, a i ≤ 1)
    (K : ℕ) (hK : budget c a K < 1)
    (A extra : ℕ → (Fin d → ℝ) → ℝ)
    (tail envelope : ℕ → (Fin d → ℝ) → ℕ → ℝ)
    (hA : ∀ k v, (∃ i, v i ≠ 0) → 0 < A k v)
    (hx : ∀ k v, 0 ≤ extra k v)
    (ht : ∀ k v, Summable (tail k v))
    (he : ∀ k v, Summable (envelope k v))
    (hp : ∀ k v n, -A k v * envelope k v n ≤ tail k v n)
    (hs : ∀ k v, (∑' n, envelope k v n) ≤ budget c a k)
    (hfinite : ∀ k, k < K → ∀ v, (∃ i, v i ≠ 0) →
      0 < A k v + extra k v + ∑' n, tail k v n) :
    ∀ k v, (∃ i, v i ≠ 0) → 0 < A k v + extra k v + ∑' n, tail k v n := by
  intro k v hv
  by_cases hk : k < K
  · exact hfinite k hk v hv
  · have hlarge : K ≤ k := Nat.le_of_not_gt hk
    exact one_shift_positive (A k v) (extra k v) (budget c a k)
      (tail k v) (envelope k v) (hA k v hv) (hx k v)
      (budget_below_one_after c a hc ha0 ha1 K k hlarge hK)
      (ht k v) (he k v) (hp k v) (hs k v)

end
end HHTShifts

#print axioms HHTShifts.budget_nonneg
#print axioms HHTShifts.budget_step_le
#print axioms HHTShifts.budget_add_le
#print axioms HHTShifts.budget_below_one_after
#print axioms HHTShifts.complex_pairing_bound
#print axioms HHTShifts.infinite_envelope_lower
#print axioms HHTShifts.one_shift_positive
#print axioms HHTShifts.all_shifts_positive
