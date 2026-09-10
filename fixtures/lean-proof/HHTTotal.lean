import Mathlib.Data.Real.Basic
import Mathlib.Order.Monotone.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Lean.Elab.Tactic.Omega

/-!
All-gap order-two positivity and a dimension-frontier recurrence.
The full order-r Fekete theorem, special functions and zero counts are NOT
formalized here. The recurrence is an explicit premise, not a global postulate.
-/
namespace HHTTotal
noncomputable section

def gapMinor (m : ℕ → ℝ) (n a b : ℕ) : ℝ :=
  m n * m (n + a + b) - m (n + a) * m (n + b)

/-- Adjacent strict log-convexity forces strictly increasing adjacent ratios. -/
theorem step_ratio_strictMono (m : ℕ → ℝ)
    (hp : ∀ n, 0 < m n)
    (hc : ∀ n, m (n+1)^2 < m n * m (n+2)) :
    StrictMono (fun n => m (n+1) / m n) := by
  apply strictMono_nat_of_lt_succ
  intro n
  apply (div_lt_div_iff₀ (hp n) (hp (n+1))).mpr
  have h := hc n
  have he : n+1+1 = n+2 := by omega
  rw [he]
  nlinarith

/-- Arbitrarily long increment ratios are strictly increasing, not just adjacent ones. -/
theorem gap_ratio_strictMono (m : ℕ → ℝ)
    (hp : ∀ n, 0 < m n)
    (hc : ∀ n, m (n+1)^2 < m n * m (n+2))
    (a : ℕ) (ha : 0 < a) : StrictMono (fun n => m (n+a) / m n) := by
  apply strictMono_nat_of_lt_succ
  intro n
  have h := step_ratio_strictMono m hp hc (show n < n+a by omega)
  have hh := (div_lt_div_iff₀ (hp n) (hp (n+a))).mp h
  apply (div_lt_div_iff₀ (hp n) (hp (n+1))).mpr
  have he : n+1+a = n+a+1 := by omega
  rw [he]
  nlinarith

/-- Every order-two minor with arbitrary positive index gaps is positive. -/
theorem all_gap_minors_positive (m : ℕ → ℝ)
    (hp : ∀ n, 0 < m n)
    (hc : ∀ n, m (n+1)^2 < m n * m (n+2))
    (n a b : ℕ) (ha : 0 < a) (hb : 0 < b) : 0 < gapMinor m n a b := by
  have h := gap_ratio_strictMono m hp hc a ha (show n < n+b by omega)
  have hh := (div_lt_div_iff₀ (hp n) (hp (n+b))).mp h
  have he : n+b+a = n+a+b := by omega
  rw [he] at hh
  unfold gapMinor
  nlinarith

/-- Square completion for the real symmetric two-by-two form. -/
theorem quadratic_square (A B C x y : ℝ) :
    A*(A*x^2+2*B*x*y+C*y^2) = (A*x+B*y)^2+(A*C-B^2)*y^2 := by
  ring

/-- Strict positive determinant and top-left entry control all nonzero directions. -/
theorem quadratic_positive (A B C x y : ℝ)
    (hA : 0 < A) (hD : 0 < A*C-B^2) (hxy : x ≠ 0 ∨ y ≠ 0) :
    0 < A*x^2+2*B*x*y+C*y^2 := by
  have hi := quadratic_square A B C x y
  by_cases hy : y = 0
  · have hx : x ≠ 0 := hxy.resolve_right (not_not_intro hy)
    subst y
    simpa using mul_pos hA (sq_pos_of_ne_zero hx)
  · have hs : 0 < (A*C-B^2)*y^2 := mul_pos hD (sq_pos_of_ne_zero hy)
    have hz := sq_nonneg (A*x+B*y)
    have hm : 0 < A*(A*x^2+2*B*x*y+C*y^2) := by linarith
    exact (mul_pos_iff_of_pos_left hA).mp hm

/-- Any two-term polynomial, at unbounded degree and shift, has positive energy. -/
theorem two_term_positive (m : ℕ → ℝ)
    (hp : ∀ n, 0 < m n)
    (hc : ∀ n, m (n+1)^2 < m n * m (n+2))
    (k e a : ℕ) (ha : 0 < a) (x y : ℝ) (hxy : x ≠ 0 ∨ y ≠ 0) :
    0 < m (k+e+e)*x^2 + 2*m (k+e+e+a)*x*y + m (k+e+e+a+a)*y^2 := by
  have h := all_gap_minors_positive m hp hc (k+e+e) a a ha ha
  unfold gapMinor at h
  apply quadratic_positive _ _ _ x y (hp (k+e+e)) _ hxy
  nlinarith

/-- A positive lower-order factor makes the dimension step exactly a log-convexity test. -/
theorem next_order_iff (higher lower left middle right : ℝ)
    (hl : 0 < lower) (hid : higher*lower = left*right-middle^2) :
    0 < higher ↔ middle^2 < left*right := by
  constructor
  · intro hh
    have hm := mul_pos hh hl
    linarith
  · intro hd
    have hm : 0 < higher*lower := by linarith
    exact (mul_pos_iff_of_pos_right hl).mp hm

/-- Positive determinant rows are strictly log-convex under the condensation identity. -/
theorem determinant_row_strict_logconvex (t : ℕ → ℕ → ℝ) (d : ℕ)
    (hpos : ∀ k, 0 < t d (k+2))
    (hnext : ∀ k, 0 < t (d+2) k)
    (hrec : ∀ k, t (d+2) k*t d (k+2) =
      t (d+1) k*t (d+1) (k+2)-(t (d+1) (k+1))^2) :
    ∀ k, (t (d+1) (k+1))^2 < t (d+1) k*t (d+1) (k+2) := by
  intro k
  exact (next_order_iff _ _ _ _ _ (hpos k) (hrec k)).mp (hnext k)

/-- In the presence of a positive preceding row, the entire next row is equivalent
    to strict log-convexity at every shift; neither side is asserted for xi. -/
theorem entire_next_row_iff (t : ℕ → ℕ → ℝ) (d : ℕ)
    (hpos : ∀ k, 0 < t d (k+2))
    (hrec : ∀ k, t (d+2) k*t d (k+2) =
      t (d+1) k*t (d+1) (k+2)-(t (d+1) (k+1))^2) :
    (∀ k, 0 < t (d+2) k) ↔
    (∀ k, (t (d+1) (k+1))^2 < t (d+1) k*t (d+1) (k+2)) := by
  constructor
  · intro hn
    exact determinant_row_strict_logconvex t d hpos hn hrec
  · intro hc k
    exact (next_order_iff _ _ _ _ _ (hpos k) (hrec k)).mpr (hc k)

/-- A concrete Hankel boundary: all adjacent order-two minors are positive. -/
theorem boundary_second_order :
    (0 : ℝ) < 1*5-2^2 ∧ (0 : ℝ) < 2*14-5^2 ∧ (0 : ℝ) < 5*40-14^2 := by
  norm_num

/-- Those three positive minors do not imply the next order is positive. -/
theorem boundary_next_order : (1 : ℝ)*4-3^2 = (-1)*5 := by
  norm_num

end
end HHTTotal

#print axioms HHTTotal.step_ratio_strictMono
#print axioms HHTTotal.gap_ratio_strictMono
#print axioms HHTTotal.all_gap_minors_positive
#print axioms HHTTotal.quadratic_square
#print axioms HHTTotal.quadratic_positive
#print axioms HHTTotal.two_term_positive
#print axioms HHTTotal.next_order_iff
#print axioms HHTTotal.determinant_row_strict_logconvex
#print axioms HHTTotal.entire_next_row_iff
#print axioms HHTTotal.boundary_second_order
#print axioms HHTTotal.boundary_next_order
