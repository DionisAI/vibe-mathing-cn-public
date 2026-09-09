import Mathlib.Data.Real.Basic
import Mathlib.Topology.Algebra.Ring.Real
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Topology.Algebra.InfiniteSum.Ring
import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
HHT-006 formalization core. The infinite-series comparison takes summability
and pointwise envelopes as explicit inputs. It does not assert anything
about zeta zeros or formalize the full spectral construction.
-/
set_option autoImplicit false
namespace HHT006

/-- Real linear coefficients can prescribe an arbitrary value at a nonreal point. -/
theorem real_linear_interpolation (x y P Q : ℝ) (hy : y ≠ 0) :
    ∃ a b : ℝ, a + b * x = P ∧ b * y = Q := by
  refine ⟨P - (Q / y) * x, Q / y, ?_, ?_⟩
  · ring
  · field_simp [hy]

/-- A pair normalized to i and -i has a strictly negative contribution. -/
theorem normalized_pair_negative (m x y : ℝ) (hm : 0 < m) (hx : 0 < x) :
    2 * m * (x * ((0 : ℝ) ^ 2 - 1 ^ 2) - 2 * y * 0 * 1) < 0 := by
  have hmx := mul_pos hm hx
  nlinarith

/-- A finite geometrically decaying budget eventually falls below any positive margin. -/
theorem geometric_budget_exists (C theta eta : ℝ)
    (hC : 0 ≤ C) (htheta : theta < 1) (heta : 0 < eta) :
    ∃ M : ℕ, C * theta ^ M < eta := by
  rcases eq_or_lt_of_le hC with hzero | hpos
  · have hCzero : C = 0 := hzero.symm
    subst C
    exact ⟨0, by simpa using heta⟩
  · obtain ⟨M, hM⟩ := exists_pow_lt_of_lt_one (div_pos heta hpos) htheta
    refine ⟨M, ?_⟩
    have h := (lt_div_iff₀ hpos).mp hM
    simpa [mul_comm] using h

/-- Sum a pointwise upper envelope over a genuine infinite series. -/
theorem infinite_envelope_upper {f mass : ℕ → ℝ} {S K : ℝ}
    (hf : Summable f) (hmass : HasSum mass S)
    (hpoint : ∀ n, f n ≤ K * mass n) :
    (∑' n, f n) ≤ K * S := by
  exact hasSum_le hpoint hf.hasSum (hmass.mul_left K)

/-- A family of localized tails eventually leaves its negative target exposed.
The pointwise bounds and summability must be proved for the intended family. -/
theorem localized_infinite_negative {f : ℕ → ℕ → ℝ} {mass : ℕ → ℝ}
    (C S theta eta : ℝ) (hC : 0 ≤ C) (hS : 0 ≤ S)
    (htheta : theta < 1) (heta : 0 < eta)
    (hf : ∀ M, Summable (f M)) (hmass : HasSum mass S)
    (hpoint : ∀ M n, f M n ≤ (C * theta ^ M) * mass n) :
    ∃ M : ℕ, -eta + (∑' n, f M n) < 0 := by
  obtain ⟨M, hM⟩ := geometric_budget_exists (C * S) theta eta
    (mul_nonneg hC hS) htheta heta
  have htail := infinite_envelope_upper (hf M) hmass (hpoint M)
  have hrewrite : (C * theta ^ M) * S = (C * S) * theta ^ M := by ring
  rw [hrewrite] at htail
  exact ⟨M, by linarith⟩

/-- The polynomial which vanishes on every finite head node. -/
noncomputable def headPoly {n : ℕ} (u : Fin n → ℝ) : Polynomial ℝ :=
  ∏ j : Fin n, (Polynomial.X - Polynomial.C (u j))

/-- Repeated nodes do not make the product polynomial identically zero. -/
theorem headPoly_ne_zero {n : ℕ} (u : Fin n → ℝ) : headPoly u ≠ 0 := by
  classical
  unfold headPoly
  apply Finset.prod_ne_zero_iff.mpr
  intro j _ hj
  have h := congrArg (fun p : Polynomial ℝ => p.coeff 1) hj
  simp at h

/-- Every designated head evaluation is zero, including arbitrary real locations. -/
theorem headPoly_eval_zero {n : ℕ} (u : Fin n → ℝ) (i : Fin n) :
    (headPoly u).eval (u i) = 0 := by
  classical
  change (Polynomial.evalRingHom (u i)) (∏ j : Fin n,
    (Polynomial.X - Polynomial.C (u j))) = 0
  rw [map_prod]
  apply Finset.prod_eq_zero (Finset.mem_univ i)
  simp

/-- The finite head has an annihilator already in dimension n+1. -/
theorem headPoly_natDegree {n : ℕ} (u : Fin n → ℝ) :
    (headPoly u).natDegree = n := by
  classical
  simpa [headPoly] using
    (Polynomial.natDegree_prod_of_monic Finset.univ
      (fun j : Fin n => Polynomial.X - Polynomial.C (u j))
      (fun j _ => Polynomial.monic_X_sub_C (u j)))

/-- No finite head can be strictly positive on polynomials of all degrees. -/
theorem finite_head_rank_obstruction {n : ℕ} (u weight : Fin n → ℝ) :
    ∃ p : Polynomial ℝ, p ≠ 0 ∧ p.natDegree ≤ n ∧
      (∑ j : Fin n, weight j * (p.eval (u j)) ^ 2) = 0 := by
  refine ⟨headPoly u, headPoly_ne_zero u, ?_, ?_⟩
  · exact (headPoly_natDegree u).le
  · apply Finset.sum_eq_zero
    intro j _
    rw [headPoly_eval_zero]
    ring

/-- Exact geometric budget for the first infinite square-spectrum fixture. -/
theorem exact_localization_margin :
    -(1120 / 1369 : ℝ) +
      (14570821445 / 105906176) * (1369 / 4096) ^ (5 : ℕ) < 0 := by
  norm_num

end HHT006

#print axioms HHT006.real_linear_interpolation
#print axioms HHT006.normalized_pair_negative
#print axioms HHT006.geometric_budget_exists
#print axioms HHT006.infinite_envelope_upper
#print axioms HHT006.localized_infinite_negative
#print axioms HHT006.headPoly_ne_zero
#print axioms HHT006.headPoly_eval_zero
#print axioms HHT006.headPoly_natDegree
#print axioms HHT006.finite_head_rank_obstruction
#print axioms HHT006.exact_localization_margin
