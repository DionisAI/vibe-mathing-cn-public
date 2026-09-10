import Mathlib.Data.Real.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.NormNum

/-
Execution status is recorded by the accompanying PR and its immutable job logs.
The finite inequalities below are generic. The spectral-growth argument,
actual-xi inputs and polynomial-to-coordinate bridge remain outside this file.
The companion runner must compile and audit this file before any kernel claim.
-/

open scoped BigOperators
namespace HHTCoefficientCone

noncomputable def lin {n : ℕ} (v a : Fin n → ℝ) : ℝ :=
  ∑ i, a i * v i

noncomputable def mix {n : ℕ} (K : Fin n → Fin n → ℝ)
    (a b : Fin n → ℝ) : ℝ :=
  ∑ i, ∑ j, a i * b j * K i j

/-- The two finite linear evaluations multiply by ordinary distributivity. -/
theorem lin_mul_lin {n : ℕ} (v w a b : Fin n → ℝ) :
    lin v a * lin w b = ∑ i, ∑ j, a i * b j * (v i * w j) := by
  classical
  calc
    lin v a * lin w b = ∑ i, ∑ j, (a i * v i) * (b j * w j) := by
      unfold lin
      rw [Finset.sum_mul]
      apply Finset.sum_congr rfl
      intro i _
      rw [Finset.mul_sum]
    _ = ∑ i, ∑ j, a i * b j * (v i * w j) := by
      apply Finset.sum_congr rfl
      intro i _
      apply Finset.sum_congr rfl
      intro j _
      ring

/-- A nonnegative coefficient vector has nonnegative linear evaluation. -/
theorem linear_nonneg {n : ℕ} (v a : Fin n → ℝ)
    (hv : ∀ i, 0 ≤ v i) (ha : ∀ i, 0 ≤ a i) : 0 ≤ lin v a := by
  classical
  unfold lin
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (ha i) (hv i))

/-- Entrywise nonnegativity suffices on the nonnegative coefficient orthant. -/
theorem mix_nonneg {n : ℕ} (K : Fin n → Fin n → ℝ) (a b : Fin n → ℝ)
    (hK : ∀ i j, 0 ≤ K i j) (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i) :
    0 ≤ mix K a b := by
  classical
  unfold mix
  apply Finset.sum_nonneg
  intro i _
  apply Finset.sum_nonneg
  intro j _
  exact mul_nonneg (mul_nonneg (ha i) (hb j)) (hK i j)

/-- The coefficient-weighted moment sum inherits a pointwise geometric bound. -/
theorem linear_upper {n : ℕ} (v r b : Fin n → ℝ) (m : ℝ)
    (hb : ∀ i, 0 ≤ b i) (h : ∀ i, v i ≤ m * r i) :
    lin v b ≤ m * lin r b := by
  classical
  calc
    lin v b ≤ ∑ i, b i * (m * r i) := by
      unfold lin
      exact Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (h i) (hb i))
    _ = m * lin r b := by
      simp only [lin, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      ring

/-- Rank-one lower bounds on entries sum to a lower bound for the square. -/
theorem mix_rank_one_lower {n : ℕ} (K : Fin n → Fin n → ℝ)
    (v b : Fin n → ℝ) (m : ℝ)
    (hb : ∀ i, 0 ≤ b i) (h : ∀ i j, v i * v j ≤ m * K i j) :
    (lin v b)^2 ≤ m * mix K b b := by
  classical
  calc
    (lin v b)^2 = ∑ i, ∑ j, b i * b j * (v i * v j) := by
      rw [pow_two, lin_mul_lin]
    _ ≤ ∑ i, ∑ j, b i * b j * (m * K i j) := by
      apply Finset.sum_le_sum
      intro i _
      apply Finset.sum_le_sum
      intro j _
      exact mul_le_mul_of_nonneg_left (h i j) (mul_nonneg (hb i) (hb j))
    _ = m * mix K b b := by
      simp only [mix, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      apply Finset.sum_congr rfl
      intro j _
      ring

/-- This controls the mixed-sign cross term; no global positive form is assumed. -/
theorem mix_cross_upper {n : ℕ} (K : Fin n → Fin n → ℝ)
    (v r a b : Fin n → ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i)
    (h : ∀ i j, K i j ≤ v i * r j) :
    mix K a b ≤ lin r b * lin v a := by
  classical
  calc
    mix K a b ≤ ∑ i, ∑ j, a i * b j * (v i * r j) := by
      unfold mix
      apply Finset.sum_le_sum
      intro i _
      apply Finset.sum_le_sum
      intro j _
      exact mul_le_mul_of_nonneg_left (h i j) (mul_nonneg (ha i) (hb j))
    _ = lin v a * lin r b := (lin_mul_lin v r a b).symm
    _ = lin r b * lin v a := mul_comm _ _

/-- Scalar square completion retaining the opposite-sign self-contribution. -/
theorem scalar_cone_bound (m c B U V A D E : ℝ)
    (hm : 0 < m) (hB : B ≤ c) (hU : 0 ≤ U) (hA : 0 ≤ A)
    (hV : V ≤ m * B) (hD : V^2 ≤ m * D) (hE : E ≤ B * U) :
    m * (c-B)^2 ≤ c^2*m + A + D + 2*c*U - 2*c*V - 2*E := by
  have h1 : 0 ≤ m * A := mul_nonneg hm.le hA
  have h2 : 0 ≤ m * (B*U-E) := mul_nonneg hm.le (sub_nonneg.mpr hE)
  have h3 : 0 ≤ m * (c-B) * U :=
    mul_nonneg (mul_nonneg hm.le (sub_nonneg.mpr hB)) hU
  have h4 : 0 ≤ m*B-V := sub_nonneg.mpr hV
  have h5 : 0 ≤ 2*m*c-V-m*B := by
    have hz : 0 ≤ m*(c-B) := mul_nonneg hm.le (sub_nonneg.mpr hB)
    nlinarith
  have h6 : 0 ≤ (m*B-V)*(2*m*c-V-m*B) := mul_nonneg h4 h5
  by_contra h
  have hbad : c^2*m + A + D + 2*c*U - 2*c*V - 2*E < m*(c-B)^2 :=
    lt_of_not_ge h
  have hneg : 0 < m*(m*(c-B)^2 -
      (c^2*m + A + D + 2*c*U - 2*c*V - 2*E)) :=
    mul_pos hm (sub_pos.mpr hbad)
  nlinarith [h1, h2, h3, h6]

/-- Arbitrary finite dimension, with all pointwise kernel hypotheses exposed. -/
theorem finite_cone_lower_bound {n : ℕ} (K : Fin n → Fin n → ℝ)
    (v r a b : Fin n → ℝ) (m c : ℝ)
    (hm : 0 < m) (hv : ∀ i, 0 ≤ v i)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i)
    (hK : ∀ i j, 0 ≤ K i j)
    (hRank : ∀ i j, v i*v j ≤ m*K i j)
    (hCross : ∀ i j, K i j ≤ v i*r j)
    (hMass : ∀ i, v i ≤ m*r i)
    (hBudget : lin r b ≤ c) :
    m*(c-lin r b)^2 ≤
      c^2*m + mix K a a + mix K b b + 2*c*lin v a - 2*c*lin v b - 2*mix K a b := by
  exact scalar_cone_bound m c (lin r b) (lin v a) (lin v b)
    (mix K a a) (mix K b b) (mix K a b) hm hBudget
    (linear_nonneg v a hv ha) (mix_nonneg K a a hK ha ha)
    (linear_upper v r b m hb hMass) (mix_rank_one_lower K v b m hb hRank)
    (mix_cross_upper K v r a b ha hb hCross)

/-- Strict budget slack yields strict positivity; equality is not silently made strict. -/
theorem strict_of_budget (m c B Q : ℝ) (hm : 0 < m)
    (hB : B < c) (hQ : m*(c-B)^2 ≤ Q) : 0 < Q := by
  have hpos : 0 < m*(c-B)^2 := mul_pos hm (pow_pos (sub_pos.mpr hB) 2)
  exact lt_of_lt_of_le hpos hQ

/-- A one-step ratio bound propagates to every natural index gap. -/
theorem geometric_shift_bound (m : ℕ → ℝ) (R : ℝ)
    (hR : 0 ≤ R) (hStep : ∀ n, m (n+1) ≤ R*m n) (n j : ℕ) :
    m (n+j) ≤ R^j*m n := by
  induction j with
  | zero => simp
  | succ j ih =>
    calc
      m (n+(j+1)) ≤ R*m (n+j) := by simpa [Nat.add_assoc] using hStep (n+j)
      _ ≤ R*(R^j*m n) := mul_le_mul_of_nonneg_left ih hR
      _ = R^(j+1)*m n := by rw [pow_succ]; ring

#print axioms HHTCoefficientCone.lin_mul_lin
#print axioms HHTCoefficientCone.linear_nonneg
#print axioms HHTCoefficientCone.mix_nonneg
#print axioms HHTCoefficientCone.linear_upper
#print axioms HHTCoefficientCone.mix_rank_one_lower
#print axioms HHTCoefficientCone.mix_cross_upper
#print axioms HHTCoefficientCone.scalar_cone_bound
#print axioms HHTCoefficientCone.finite_cone_lower_bound
#print axioms HHTCoefficientCone.strict_of_budget
#print axioms HHTCoefficientCone.geometric_shift_bound

/-- Exact squared distance to a nonempty closed real interval. -/
noncomputable def boxSq (center lo hi : ℝ) : ℝ :=
  if center < lo then (lo-center)^2 else if hi < center then (center-hi)^2 else 0

/-- Every point in the interval obeys its nearest-point squared lower bound. -/
theorem box_square_lower (center lo hi x : ℝ) (hlo : lo ≤ x) (hhi : x ≤ hi) :
    boxSq center lo hi ≤ (x-center)^2 := by
  unfold boxSq
  split_ifs with hleft hright
  · have ha : 0 ≤ x-lo := sub_nonneg.mpr hlo
    have hb : 0 ≤ x+lo-2*center := by linarith
    nlinarith [mul_nonneg ha hb]
  · have ha : 0 ≤ hi-x := sub_nonneg.mpr hhi
    have hb : 0 ≤ 2*center-x-hi := by linarith
    nlinarith [mul_nonneg ha hb]
  · exact sq_nonneg _

/-- Keep BOTH self-terms: the earlier B<=c hypothesis is unnecessary here. -/
theorem scalar_balance_lower (c B u v A D E : ℝ)
    (hA : u^2 ≤ A) (hD : v^2 ≤ D) (hE : E ≤ B*u) :
    (c-v)^2 + (u-(B-c))^2 - (B-c)^2 ≤
      c^2 + A + D + 2*c*u - 2*c*v - 2*E := by
  nlinarith

/-- Exact rectangular minimization of the lower quadratic, not of the unknown form. -/
theorem scalar_rectangle_lower (c B u v A D E ua ub va vb : ℝ)
    (hA : u^2 ≤ A) (hD : v^2 ≤ D) (hE : E ≤ B*u)
    (hu0 : ua ≤ u) (hu1 : u ≤ ub) (hv0 : va ≤ v) (hv1 : v ≤ vb) :
    boxSq c va vb + boxSq (B-c) ua ub - (B-c)^2 ≤
      c^2 + A + D + 2*c*u - 2*c*v - 2*E := by
  have hbase := scalar_balance_lower c B u v A D E hA hD hE
  have hu := box_square_lower (B-c) ua ub u hu0 hu1
  have hv := box_square_lower c va vb v hv0 hv1
  nlinarith

/-- Arbitrary normalized finite kernel; rank-one and mixed bounds are exposed premises. -/
theorem finite_rectangle_lower {n : ℕ} (K : Fin n → Fin n → ℝ)
    (v r a b : Fin n → ℝ) (c ua ub va vb : ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i)
    (hRank : ∀ i j, v i*v j ≤ K i j)
    (hCross : ∀ i j, K i j ≤ v i*r j)
    (hu0 : ua ≤ lin v a) (hu1 : lin v a ≤ ub)
    (hv0 : va ≤ lin v b) (hv1 : lin v b ≤ vb) :
    boxSq c va vb + boxSq (lin r b-c) ua ub - (lin r b-c)^2 ≤
      c^2 + mix K a a + mix K b b + 2*c*lin v a - 2*c*lin v b - 2*mix K a b := by
  have hAA : (lin v a)^2 ≤ mix K a a := by
    simpa only [one_mul] using
      (mix_rank_one_lower K v a 1 ha (by intro i j; simpa only [one_mul] using hRank i j))
  have hBB : (lin v b)^2 ≤ mix K b b := by
    simpa only [one_mul] using
      (mix_rank_one_lower K v b 1 hb (by intro i j; simpa only [one_mul] using hRank i j))
  exact scalar_rectangle_lower c (lin r b) (lin v a) (lin v b)
    (mix K a a) (mix K b b) (mix K a b) ua ub va vb
    hAA hBB (mix_cross_upper K v r a b ha hb hCross) hu0 hu1 hv0 hv1

/-- Positive same-sign mass can overcome B>c; all cross terms remain present. -/
theorem rescue_lower (c B u v L : ℝ) (hL : 0 ≤ L)
    (hEnough : 2*(B-c) ≤ L) (hu : L ≤ u) :
    L*(L-2*(B-c)) ≤ (c-v)^2 + (u-(B-c))^2 - (B-c)^2 := by
  have ha : 0 ≤ u-L := sub_nonneg.mpr hu
  have hb : 0 ≤ u+L-2*(B-c) := by linarith
  nlinarith [mul_nonneg ha hb, sq_nonneg (c-v)]

/-- A supplied positive lower adjacent-ratio bound propagates to every gap. -/
theorem geometric_lower_bound (m : ℕ → ℝ) (l : ℝ)
    (hl : 0 ≤ l) (hStep : ∀ n, l*m n ≤ m (n+1)) (n j : ℕ) :
    l^j*m n ≤ m (n+j) := by
  induction j with
  | zero => simp
  | succ j ih =>
    calc
      l^(j+1)*m n = l*(l^j*m n) := by rw [pow_succ]; ring
      _ ≤ l*m (n+j) := mul_le_mul_of_nonneg_left ih hl
      _ ≤ m (n+(j+1)) := by simpa only [Nat.add_assoc] using hStep (n+j)

/-- Exact all-N rescued-family margin once the analytic ratio interval is supplied. -/
theorem rescued_family_margin :
    (1568/625 : ℝ)*((1568/625)-2) = 498624/390625 ∧
    (1 : ℝ) < 498624/390625 := by
  norm_num

#print axioms HHTCoefficientCone.box_square_lower
#print axioms HHTCoefficientCone.scalar_balance_lower
#print axioms HHTCoefficientCone.scalar_rectangle_lower
#print axioms HHTCoefficientCone.finite_rectangle_lower
#print axioms HHTCoefficientCone.rescue_lower
#print axioms HHTCoefficientCone.geometric_lower_bound
#print axioms HHTCoefficientCone.rescued_family_margin

end HHTCoefficientCone
