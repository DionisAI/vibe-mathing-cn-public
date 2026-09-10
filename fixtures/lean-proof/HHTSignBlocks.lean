import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Multilinear.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
Finite ordered positive compression, with arbitrary finite block sizes.
The complete actual-xi input, strict Fekete criterion, and Sylvester criterion
remain stated external inputs to the prose corollary. No assertion about xi
is introduced into this file. The determinant expansion itself is proved.
-/
namespace HHTSignBlocks
noncomputable section
open scoped BigOperators

/-- Expand a determinant independently along the sum defining every row. -/
theorem det_rows_sum {d : ℕ} (α : Fin d → Type)
    [∀ i, Fintype (α i)] (A : (i : Fin d) → α i → Fin d → ℝ) :
    Matrix.det (fun i j => ∑ a : α i, A i a j) =
      ∑ f : ((i : Fin d) → α i), Matrix.det (fun i j => A i (f i) j) := by
  classical
  simpa only [Matrix.det, Finset.sum_apply] using
    (Matrix.detRowAlternating (n := Fin d) (R := ℝ)).toMultilinearMap.map_sum A

/-- Column multilinearity is obtained by transposing the row expansion. -/
theorem det_columns_sum {d : ℕ} (β : Fin d → Type)
    [∀ j, Fintype (β j)] (A : (j : Fin d) → β j → Fin d → ℝ) :
    Matrix.det (fun i j => ∑ b : β j, A j b i) =
      ∑ g : ((j : Fin d) → β j), Matrix.det (fun i j => A j (g j) i) := by
  classical
  calc
    _ = Matrix.det (fun j i => ∑ b : β j, A j b i) :=
      (Matrix.det_transpose _).symm
    _ = ∑ g : ((j : Fin d) → β j), Matrix.det (fun j i => A j (g j) i) :=
      det_rows_sum β A
    _ = _ := by
      apply Finset.sum_congr rfl
      intro g _
      exact Matrix.det_transpose _

/-- Scaling independently on the two axes extracts two positive weight products. -/
theorem det_weighted {d : ℕ} (A : Matrix (Fin d) (Fin d) ℝ)
    (w v : Fin d → ℝ) :
    Matrix.det (fun i j => w i * v j * A i j) =
      (∏ i, w i) * (∏ j, v j) * Matrix.det A := by
  classical
  have h := Matrix.det_mul_column w (fun i j => v j * A i j)
  have hv := Matrix.det_mul_row v A
  simpa only [Matrix.of_apply, ← mul_assoc, hv] using h

/-- Full double mixing identity; the choices may have different finite types per block. -/
theorem det_double_mix {d : ℕ} (α β : Fin d → Type)
    [∀ i, Fintype (α i)] [∀ j, Fintype (β j)]
    (w : (i : Fin d) → α i → ℝ) (v : (j : Fin d) → β j → ℝ)
    (A : (i : Fin d) → α i → (j : Fin d) → β j → ℝ) :
    Matrix.det (fun i j => ∑ a : α i, ∑ b : β j, w i a * v j b * A i a j b) =
      ∑ f : ((i : Fin d) → α i), ∑ g : ((j : Fin d) → β j),
        (∏ i, w i (f i)) * (∏ j, v j (g j)) *
          Matrix.det (fun i j => A i (f i) j (g j)) := by
  classical
  rw [det_rows_sum α]
  apply Finset.sum_congr rfl
  intro f _
  rw [det_columns_sum β]
  apply Finset.sum_congr rfl
  intro g _
  exact det_weighted (fun i j => A i (f i) j (g j)) _ _

/-- A finite, nonempty sum of strictly positive selected determinants is positive. -/
theorem double_mix_positive {d : ℕ} (α β : Fin d → Type)
    [∀ i, Fintype (α i)] [∀ j, Fintype (β j)]
    [∀ i, Nonempty (α i)] [∀ j, Nonempty (β j)]
    (w : (i : Fin d) → α i → ℝ) (v : (j : Fin d) → β j → ℝ)
    (A : (i : Fin d) → α i → (j : Fin d) → β j → ℝ)
    (hw : ∀ i a, 0 < w i a) (hv : ∀ j b, 0 < v j b)
    (hA : ∀ f g, 0 < Matrix.det (fun i j => A i (f i) j (g j))) :
    0 < Matrix.det (fun i j => ∑ a : α i, ∑ b : β j, w i a * v j b * A i a j b) := by
  classical
  rw [det_double_mix α β w v A]
  apply Finset.sum_pos
  · intro f _
    apply Finset.sum_pos
    · intro g _
      exact mul_pos (mul_pos
        (Finset.prod_pos (fun i _ => hw i (f i)))
        (Finset.prod_pos (fun j _ => hv j (g j)))) (hA f g)
    · exact Finset.univ_nonempty
  · exact Finset.univ_nonempty

/-- Ordered disjoint blocks make every selected index function strictly increasing. -/
theorem ordered_choice {d : ℕ} (α : Fin d → Type)
    (e : (i : Fin d) → α i → ℕ)
    (he : ∀ i j, i < j → ∀ a b, e i a < e j b)
    (f : (i : Fin d) → α i) : StrictMono (fun i => e i (f i)) := by
  intro i j hij
  exact he i j hij (f i) (f j)

/-- Compression positivity follows from the actual selected-minor hypothesis,
not from assuming positivity of the already-compressed matrix. -/
theorem ordered_compression_det_positive {d : ℕ}
    (α β : Fin d → Type)
    [∀ i, Fintype (α i)] [∀ j, Fintype (β j)]
    [∀ i, Nonempty (α i)] [∀ j, Nonempty (β j)]
    (K : ℕ → ℕ → ℝ) (e : (i : Fin d) → α i → ℕ)
    (f : (j : Fin d) → β j → ℕ)
    (w : (i : Fin d) → α i → ℝ) (v : (j : Fin d) → β j → ℝ)
    (he : ∀ i j, i < j → ∀ a b, e i a < e j b)
    (hf : ∀ i j, i < j → ∀ a b, f i a < f j b)
    (hw : ∀ i a, 0 < w i a) (hv : ∀ j b, 0 < v j b)
    (hK : ∀ I J : Fin d → ℕ, StrictMono I → StrictMono J →
      0 < Matrix.det (fun i j => K (I i) (J j))) :
    0 < Matrix.det (fun i j => ∑ a : α i, ∑ b : β j,
      w i a * v j b * K (e i a) (f j b)) := by
  apply double_mix_positive α β w v (fun i a j b => K (e i a) (f j b)) hw hv
  intro I J
  exact hK _ _ (ordered_choice α e he I) (ordered_choice β f hf J)

/-- Expanding the compressed quadratic form gives the original weighted directions. -/
theorem quadratic_regroup {d : ℕ} (α : Fin d → Type)
    [∀ i, Fintype (α i)]
    (K : (i : Fin d) → α i → (j : Fin d) → α j → ℝ)
    (w : (i : Fin d) → α i → ℝ) (s : Fin d → ℝ) :
    (∑ i, ∑ j, s i * s j * (∑ a : α i, ∑ b : α j, w i a * w j b * K i a j b)) =
    ∑ i, ∑ j, ∑ a : α i, ∑ b : α j,
      (s i * w i a) * (s j * w j b) * K i a j b := by
  classical
  simp only [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro a _
  apply Finset.sum_congr rfl
  intro b _
  ring

/-- Ordered compression is symmetric when the underlying kernel is symmetric. -/
theorem compression_symmetric {d : ℕ} (α : Fin d → Type)
    [∀ i, Fintype (α i)] (K : ℕ → ℕ → ℝ)
    (e : (i : Fin d) → α i → ℕ) (w : (i : Fin d) → α i → ℝ)
    (hK : ∀ i j, K i j = K j i) (i j : Fin d) :
    (∑ a : α i, ∑ b : α j, w i a * w j b * K (e i a) (e j b)) =
    ∑ b : α j, ∑ a : α i, w j b * w i a * K (e j b) (e i a) := by
  classical
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro b _
  apply Finset.sum_congr rfl
  intro a _
  rw [hK (e i a) (e j b)]
  ring

/-- The TP2 boundary has a negative three-term direction with two sign changes. -/
theorem alternating_boundary :
    (1:ℝ)*3^2 + 2*2*3*(-4) + 2*5*3*1 + 5*(-4)^2 + 2*14*(-4)*1 + 40*1^2 = -1 := by
  norm_num

#print axioms HHTSignBlocks.det_rows_sum
#print axioms HHTSignBlocks.det_columns_sum
#print axioms HHTSignBlocks.det_weighted
#print axioms HHTSignBlocks.det_double_mix
#print axioms HHTSignBlocks.double_mix_positive
#print axioms HHTSignBlocks.ordered_choice
#print axioms HHTSignBlocks.ordered_compression_det_positive
#print axioms HHTSignBlocks.quadratic_regroup
#print axioms HHTSignBlocks.compression_symmetric
#print axioms HHTSignBlocks.alternating_boundary
end
end HHTSignBlocks
