import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Push
import Lean.Elab.Tactic.Omega
import Mathlib.Tactic.NormNum

/-! Four fixed phase directions detect a nonreal pair despite a contracting
infinite tail. Spectral interpolation and the actual-xi correspondence are
explicit external links, not postulates added to the environment. -/
set_option autoImplicit false
namespace HHTCofinal
noncomputable section
open scoped BigOperators
open Filter

/-- Multiplication by a unit phase preserves the squared Euclidean norm. -/
theorem rotation_circle (a b x y : ℝ) (hab : a*a+b*b=1) (hxy : x*x+y*y=1) :
    (a*x-b*y)^2 + (a*y+b*x)^2=1 := by
  calc
    (a*x-b*y)^2 + (a*y+b*x)^2 = (a*a+b*b)*(x*x+y*y) := by ring
    _ = 1 := by rw [hab,hxy]; ring

def phase (a b : ℝ) : ℕ → ℝ × ℝ
  | 0 => (1,0)
  | n+1 => (a*(phase a b n).1-b*(phase a b n).2,
             a*(phase a b n).2+b*(phase a b n).1)

/-- All powers have unit phase; no equidistribution or irrational angle is assumed. -/
theorem phase_circle (a b : ℝ) (hab : a*a+b*b=1) (n : ℕ) :
    (phase a b n).1^2+(phase a b n).2^2=1 := by
  induction n with
  | zero => simp [phase]
  | succ n ih =>
    simpa only [phase] using rotation_circle a b (phase a b n).1 (phase a b n).2
      hab (by nlinarith [ih])

/-- The four real directions cannot all remain nonnegative under error below one. -/
theorem four_phase_negative (x y E q0 qi qp qm : ℝ)
    (hcircle : x*x+y*y=1) (hE : E<1)
    (h0 : q0 ≤ 2*x+E) (hi : qi ≤ -2*x+E)
    (hp : qp ≤ -4*y+E) (hm : qm ≤ 4*y+E) :
    q0<0 ∨ qi<0 ∨ qp<0 ∨ qm<0 := by
  by_contra h
  push_neg at h
  rcases h with ⟨h0n,hin,hpn,hmn⟩
  have hxlo : 0 ≤ x+1/2 := by linarith
  have hxhi : 0 ≤ 1/2-x := by linarith
  have hylo : 0 ≤ y+1/4 := by linarith
  have hyhi : 0 ≤ 1/4-y := by linarith
  have hsx := mul_nonneg hxlo hxhi
  have hsy := mul_nonneg hylo hyhi
  nlinarith

/-- A pointwise upper envelope controls the genuine infinite sum. -/
theorem infinite_upper (tail envelope : ℕ → ℝ)
    (ht : Summable tail) (he : Summable envelope)
    (hp : ∀ n, tail n ≤ envelope n) :
    (∑' n, tail n) ≤ ∑' n, envelope n := by
  exact hasSum_le hp ht.hasSum he.hasSum

/-- Full infinite sums in four directions, not finite-prefix sums, detect negativity. -/
theorem infinite_four_negative (x y E : ℝ) (tail : Fin 4 → ℕ → ℝ)
    (envelope : ℕ → ℝ) (hcircle : x*x+y*y=1) (hE : E<1)
    (ht : ∀ i, Summable (tail i)) (he : Summable envelope)
    (hp : ∀ i n, tail i n ≤ envelope n) (hs : (∑' n, envelope n) ≤ E) :
    2*x+(∑' n, tail 0 n)<0 ∨ -2*x+(∑' n, tail 1 n)<0 ∨
    -4*y+(∑' n, tail 2 n)<0 ∨ 4*y+(∑' n, tail 3 n)<0 := by
  have hbound : ∀ i, (∑' n, tail i n) ≤ E := fun i =>
    (infinite_upper (tail i) envelope (ht i) he (hp i)).trans hs
  apply four_phase_negative x y E _ _ _ _ hcircle hE
  · linarith [hbound 0]
  · linarith [hbound 1]
  · linarith [hbound 2]
  · linarith [hbound 3]

/-- The normalized tail budget decreases with shift. -/
theorem geometric_step (C a : ℝ) (hC : 0 ≤ C) (ha0 : 0 ≤ a)
    (ha1 : a ≤ 1) (k : ℕ) : C*a^(k+1) ≤ C*a^k := by
  rw [pow_succ]
  exact mul_le_mul_of_nonneg_left
    (mul_le_of_le_one_right (pow_nonneg ha0 k) ha1) hC

/-- An observed strict threshold controls every later shift. -/
theorem geometric_after (C a : ℝ) (hC : 0 ≤ C) (ha0 : 0 ≤ a)
    (ha1 : a ≤ 1) (K k : ℕ) (hk : K ≤ k) (hK : C*a^K<1) : C*a^k<1 := by
  have h : ∀ n, C*a^(K+n) ≤ C*a^K := by
    intro n
    induction n with
    | zero => simp
    | succ n ih => exact (geometric_step C a hC ha0 ha1 (K+n)).trans ih
  have hh := h (k-K)
  rw [Nat.add_sub_of_le hk] at hh
  exact lt_of_le_of_lt hh hK

/-- A finite threshold exists for every strict contraction. -/
theorem geometric_threshold_exists (C a : ℝ) (ha0 : 0 ≤ a) (ha1 : a<1) :
    ∃ K : ℕ, ∀ k ≥ K, C*a^k<1 := by
  have hpow := tendsto_pow_atTop_nhds_zero_of_lt_one ha0 ha1
  have hlim : Tendsto (fun k : ℕ => C*a^k) atTop (nhds (0:ℝ)) := by
    simpa only [mul_zero] using (tendsto_const_nhds.mul hpow :
      Tendsto (fun k : ℕ => C*a^k) atTop (nhds (C*0)))
  exact eventually_atTop.1 ((tendsto_order.1 hlim).2 1 (by norm_num))

/-- Every sufficiently late shift has a negative full direction, among four fixed choices. -/
theorem eventual_four_negative (C a : ℝ) (ha0 : 0 ≤ a) (ha1 : a<1)
    (x y : ℕ → ℝ) (tail : ℕ → Fin 4 → ℕ → ℝ)
    (envelope : ℕ → ℕ → ℝ)
    (hc : ∀ k, x k*x k+y k*y k=1)
    (ht : ∀ k i, Summable (tail k i)) (he : ∀ k, Summable (envelope k))
    (hp : ∀ k i n, tail k i n ≤ envelope k n)
    (hs : ∀ k, (∑' n, envelope k n) ≤ C*a^k) :
    ∃ K : ℕ, ∀ k ≥ K,
    2*x k+(∑' n, tail k 0 n)<0 ∨ -2*x k+(∑' n, tail k 1 n)<0 ∨
    -4*y k+(∑' n, tail k 2 n)<0 ∨ 4*y k+(∑' n, tail k 3 n)<0 := by
  obtain ⟨K,hK⟩ := geometric_threshold_exists C a ha0 ha1
  refine ⟨K,?_⟩
  intro k hk
  exact infinite_four_negative (x k) (y k) (C*a^k) (tail k) (envelope k)
    (hc k) (hK k hk) (ht k) (he k) (hp k) (hs k)

def hankel (mu : ℕ → ℝ) (d k : ℕ) : Matrix (Fin d) (Fin d) ℝ :=
  fun i j => mu (k+i.val+j.val)

/-- Larger positive semidefinite Hankel blocks restrict to smaller prefix blocks. -/
theorem hankel_psd_prefix (mu : ℕ → ℝ) (D d k : ℕ)
    (hd : D ≤ d) (hp : (hankel mu d k).PosSemidef) :
    (hankel mu D k).PosSemidef := by
  let e : Fin D → Fin d := fun i => ⟨i.val,lt_of_lt_of_le i.isLt hd⟩
  simpa only [hankel,Matrix.submatrix,e] using hp.submatrix e

/-- A later shift is an actual principal submatrix of a larger earlier-shift block. -/
theorem hankel_psd_shift (mu : ℕ → ℝ) (d M k : ℕ)
    (hp : (hankel mu (d+M) k).PosSemidef) :
    (hankel mu d (k+2*M)).PosSemidef := by
  let e : Fin d → Fin (d+M) := fun i => ⟨M+i.val,by omega⟩
  have hh := hp.submatrix e
  have heq : (hankel mu (d+M) k).submatrix e e = hankel mu d (k+2*M) := by
    funext i j
    dsimp only [hankel,Matrix.submatrix,e]
    congr 1
    omega
  rw [heq] at hh
  exact hh

/-- One fixed-size obstruction at all late shifts gives a size obstruction at EVERY shift. -/
theorem uniform_dimension_obstruction (mu : ℕ → ℝ) (D K : ℕ)
    (hbad : ∀ k ≥ K, ¬ (hankel mu D k).PosSemidef) :
    ∃ B : ℕ, ∀ d ≥ B, ∀ k : ℕ, ¬ (hankel mu d k).PosSemidef := by
  refine ⟨D+(K+1)/2,?_⟩
  intro d hd k hp
  have hprefix := hankel_psd_prefix mu (D+(K+1)/2) d k hd hp
  have hshift := hankel_psd_shift mu D ((K+1)/2) k hprefix
  exact hbad (k+2*((K+1)/2)) (by omega) hshift

/-- Unbounded positive block sizes suffice; their successful shifts may be arbitrary.
Spectral interpolation supplies an eventual obstruction if a nonreal node exists. -/
theorem dimension_cofinal_no_eventual_obstruction (mu : ℕ → ℝ)
    (hcofinal : ∀ D : ℕ, ∃ d k : ℕ, D ≤ d ∧ (hankel mu d k).PosSemidef) :
    ¬ ∃ D K : ℕ, ∀ k ≥ K, ¬ (hankel mu D k).PosSemidef := by
  rintro ⟨D,K,hbad⟩
  obtain ⟨B,hB⟩ := uniform_dimension_obstruction mu D K hbad
  obtain ⟨d,k,hd,hpos⟩ := hcofinal B
  exact hB d hd k hpos

end
end HHTCofinal

#print axioms HHTCofinal.rotation_circle
#print axioms HHTCofinal.phase_circle
#print axioms HHTCofinal.four_phase_negative
#print axioms HHTCofinal.infinite_upper
#print axioms HHTCofinal.infinite_four_negative
#print axioms HHTCofinal.geometric_step
#print axioms HHTCofinal.geometric_after
#print axioms HHTCofinal.geometric_threshold_exists
#print axioms HHTCofinal.eventual_four_negative
#print axioms HHTCofinal.hankel_psd_prefix
#print axioms HHTCofinal.hankel_psd_shift
#print axioms HHTCofinal.uniform_dimension_obstruction
#print axioms HHTCofinal.dimension_cofinal_no_eventual_obstruction
