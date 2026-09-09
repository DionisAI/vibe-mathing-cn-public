import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Lean.Elab.Tactic.Omega

/-!
Algebraic components of the exact finite-jet twins construction.
The root counts, disk geometry and entire products are NOT asserted here.
Newton recurrences are explicit hypotheses, not claims about actual xi zeros.
-/
set_option autoImplicit false
namespace HHTFiniteJet

/-- An additive term of degree N does not change coefficients below N. -/
theorem high_perturbation_coeff (p : Polynomial ℝ) (e : ℝ) (N k : ℕ)
    (hk : k < N) :
    (p + Polynomial.C e * Polynomial.X ^ N).coeff k = p.coeff k := by
  simp [Polynomial.coeff_add, Polynomial.coeff_C_mul, Polynomial.coeff_X_pow,
    ne_of_lt hk]

/-- Moving only the constant term preserves all positive-degree coefficients. -/
theorem constant_perturbation_coeff (p : Polynomial ℝ) (e : ℝ) (k : ℕ)
    (hk : k ≠ 0) : (p + Polynomial.C e).coeff k = p.coeff k := by
  simp [Polynomial.coeff_add, Polynomial.coeff_C, hk]

/-- Two sequences satisfying Newton recurrences share the same finite prefix. -/
theorem newton_prefix_unique (c d s t : ℕ → ℝ) (N : ℕ)
    (hc : ∀ k, 1 ≤ k → k ≤ N → c k = d k)
    (hs : ∀ n, s (n+1) = -((n+1 : ℕ) : ℝ) * c (n+1) -
      Finset.sum (Finset.range n) (fun i => c (i+1) * s (n-i)))
    (ht : ∀ n, t (n+1) = -((n+1 : ℕ) : ℝ) * d (n+1) -
      Finset.sum (Finset.range n) (fun i => d (i+1) * t (n-i))) :
    ∀ k, 1 ≤ k → k ≤ N → s k = t k := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro hk hN
    cases k with
    | zero => omega
    | succ n =>
      have hsum :
          Finset.sum (Finset.range n) (fun i => c (i+1) * s (n-i)) =
          Finset.sum (Finset.range n) (fun i => d (i+1) * t (n-i)) := by
        apply Finset.sum_congr rfl
        intro i hi
        have hir := Finset.mem_range.mp hi
        rw [hc (i+1) (by omega) (by omega),
          ih (n-i) (by omega) (by omega) (by omega)]
      rw [hs n, ht n, hc (n+1) (by omega) hN, hsum]

/-- The first differing Newton coefficient produces its exact power-sum difference. -/
theorem next_newton_difference (c d s t : ℕ → ℝ) (N : ℕ) (delta : ℝ)
    (hc : ∀ k, 1 ≤ k → k < N → c k = d k)
    (hp : ∀ k, 1 ≤ k → k < N → s k = t k)
    (hs : s N = -(N : ℝ) * c N -
      Finset.sum (Finset.range (N-1)) (fun i => c (i+1) * s (N-1-i)))
    (ht : t N = -(N : ℝ) * d N -
      Finset.sum (Finset.range (N-1)) (fun i => d (i+1) * t (N-1-i)))
    (hd : d N - c N = delta) : t N - s N = -(N : ℝ) * delta := by
  have hsum :
      Finset.sum (Finset.range (N-1)) (fun i => c (i+1) * s (N-1-i)) =
      Finset.sum (Finset.range (N-1)) (fun i => d (i+1) * t (N-1-i)) := by
    apply Finset.sum_congr rfl
    intro i hi
    have hir := Finset.mem_range.mp hi
    rw [hc (i+1) (by omega) (by omega), hp (N-1-i) (by omega) (by omega)]
  rw [ht, hs, hsum, ← hd]
  ring

/-- A shared power-sum prefix gives exactly equal shifted Hankel entries. -/
theorem hankel_entries_matching (s t : ℕ → ℝ) (L d k : ℕ)
    (hp : ∀ n, 1 ≤ n → n < 2*L → s n = t n)
    (hsize : k + 2*d ≤ 2*L) (i j : Fin d) :
    s (k + i.val + j.val + 1) = t (k + i.val + j.val + 1) := by
  apply hp
  · omega
  · have hi := i.isLt
    have hj := j.isLt
    omega

/-- A nonnegative base polynomial plus positive epsilon has no real zero there. -/
theorem positive_perturbation_no_zero (a epsilon : ℝ)
    (ha : 0 ≤ a) (he : 0 < epsilon) : a + epsilon ≠ 0 := by
  exact ne_of_gt (add_pos_of_nonneg_of_pos ha he)

end HHTFiniteJet

#print axioms HHTFiniteJet.high_perturbation_coeff
#print axioms HHTFiniteJet.constant_perturbation_coeff
#print axioms HHTFiniteJet.newton_prefix_unique
#print axioms HHTFiniteJet.next_newton_difference
#print axioms HHTFiniteJet.hankel_entries_matching
#print axioms HHTFiniteJet.positive_perturbation_no_zero
