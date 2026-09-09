import Mathlib.Data.Real.Basic
import Mathlib.Topology.Algebra.Ring.Real
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Topology.Algebra.InfiniteSum.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
An infinite-series, all-directions positivity theorem for a two-dimensional
Hankel quadratic form. Analytic root/count inputs are explicit hypotheses,
not declarations about zeta. No finite truncation stands for an infinite sum.
-/
namespace HHT005

/-- Real part of (x+i*y)*(a+b*(x+i*y))^2, as moment coordinates. -/
def term (x y a b : ℝ) : ℝ :=
  x * a ^ 2 + (x ^ 2 - y ^ 2) * (2 * a * b) +
    (x ^ 3 - 3 * x * y ^ 2) * b ^ 2

/-- The possible negative contribution, before multiplying by slope squared. -/
noncomputable def loss (x y : ℝ) : ℝ := ((x ^ 2 + y ^ 2) / x) * y ^ 2

/-- Completing the square gives a one-sided bound uniform in a and b. -/
theorem term_lower (x y a b : ℝ) (hx : 0 < x) :
    -(b ^ 2) * loss x y ≤ term x y a b := by
  have hid : x * (term x y a b + b ^ 2 * loss x y) =
      (x * (a + b * x) - y * (b * y)) ^ 2 := by
    unfold term loss
    field_simp [ne_of_gt hx]
    ring
  have hmul : 0 ≤ x * (term x y a b + b ^ 2 * loss x y) := by
    rw [hid]
    exact sq_nonneg _
  have h := nonneg_of_mul_nonneg_right hmul hx
  linarith

/-- Three summable moments imply summability of every quadratic direction. -/
theorem term_summable {x y : ℕ → ℝ}
    (h0 : Summable x)
    (h1 : Summable (fun n => x n ^ 2 - y n ^ 2))
    (h2 : Summable (fun n => x n ^ 3 - 3 * x n * y n ^ 2)) (a b : ℝ) :
    Summable (fun n => term (x n) (y n) a b) := by
  exact ((h0.mul_right (a ^ 2)).add (h1.mul_right (2 * a * b))).add
    (h2.mul_right (b ^ 2))

/-- The actual infinite sum equals the quadratic form of the three tail moments. -/
theorem term_hasSum {x y : ℕ → ℝ}
    (h0 : Summable x)
    (h1 : Summable (fun n => x n ^ 2 - y n ^ 2))
    (h2 : Summable (fun n => x n ^ 3 - 3 * x n * y n ^ 2)) (a b : ℝ) :
    HasSum (fun n => term (x n) (y n) a b)
      ((∑' n, x n) * a ^ 2 + (∑' n, (x n ^ 2 - y n ^ 2)) * (2 * a * b) +
        (∑' n, (x n ^ 3 - 3 * x n * y n ^ 2)) * b ^ 2) := by
  exact ((h0.hasSum.mul_right (a ^ 2)).add (h1.hasSum.mul_right (2 * a * b))).add
    (h2.hasSum.mul_right (b ^ 2))

/-- Summing the local bound is valid for the whole infinite tail. -/
theorem infinite_tail_lower {x y : ℕ → ℝ}
    (hx : ∀ n, 0 < x n)
    (h0 : Summable x)
    (h1 : Summable (fun n => x n ^ 2 - y n ^ 2))
    (h2 : Summable (fun n => x n ^ 3 - 3 * x n * y n ^ 2))
    (hloss : Summable (fun n => loss (x n) (y n))) (a b : ℝ) :
    -(b ^ 2) * (∑' n, loss (x n) (y n)) ≤
      (∑' n, x n) * a ^ 2 + (∑' n, (x n ^ 2 - y n ^ 2)) * (2 * a * b) +
        (∑' n, (x n ^ 3 - 3 * x n * y n ^ 2)) * b ^ 2 := by
  exact hasSum_le (fun n => term_lower (x n) (y n) a b (hx n))
    (hloss.hasSum.mul_left (-(b ^ 2))) (term_hasSum h0 h1 h2 a b)

/-- An explicit Schur margin dominates a loss on the slope coefficient only. -/
theorem damped_two_node_positive (u v L a b : ℝ)
    (hu : 0 < u) (hv : 0 < v)
    (hL : L < u * v * (u - v) ^ 2 / (u + v))
    (hab : a ≠ 0 ∨ b ≠ 0) :
    0 < u * (a + b * u) ^ 2 + v * (a + b * v) ^ 2 - L * b ^ 2 := by
  have huv : 0 < u + v := add_pos hu hv
  have hc : 0 < u * v * (u - v) ^ 2 - (u + v) * L := by
    have hh := (lt_div_iff₀ huv).mp hL
    nlinarith
  have hid :
      (u + v) * (u * (a + b * u) ^ 2 + v * (a + b * v) ^ 2 - L * b ^ 2) =
      ((u + v) * a + (u ^ 2 + v ^ 2) * b) ^ 2 +
        (u * v * (u - v) ^ 2 - (u + v) * L) * b ^ 2 := by ring
  by_cases hb : b = 0
  · have ha : a ≠ 0 := hab.resolve_right (not_not.mpr hb)
    subst b
    simpa [add_mul] using mul_pos huv (sq_pos_of_ne_zero ha)
  · have hp := mul_pos hc (sq_pos_of_ne_zero hb)
    have hright : 0 < ((u + v) * a + (u ^ 2 + v ^ 2) * b) ^ 2 +
        (u * v * (u - v) ^ 2 - (u + v) * L) * b ^ 2 :=
      add_pos_of_nonneg_of_pos (sq_nonneg _) hp
    rw [← hid] at hright
    exact pos_of_mul_pos_right hright (le_of_lt huv)

/-- Interval bounds for the first two ordinates give a certified Schur lower bound. -/
theorem two_node_interval_schur (u v : ℝ)
    (hu0 : 1 / 225 ≤ u) (hu1 : u ≤ 1 / 196)
    (hv0 : 1 / 484 ≤ v) (hv1 : v ≤ 1 / 441) :
    (64 / 10838953125 : ℝ) ≤ u * v * (u - v) ^ 2 / (u + v) := by
  have hu : 0 < u := by linarith
  have hv : 0 < v := by linarith
  have huv : 0 < u + v := add_pos hu hv
  have hprod : (1 / 225 : ℝ) * (1 / 484) ≤ u * v :=
    mul_le_mul hu0 hv0 (by norm_num) (le_of_lt hu)
  have hgap : (1 / 225 : ℝ) - 1 / 441 ≤ u - v := by linarith
  have hgap0 : 0 ≤ (1 / 225 : ℝ) - 1 / 441 := by norm_num
  have hsq : ((1 / 225 : ℝ) - 1 / 441) ^ 2 ≤ (u - v) ^ 2 := by
    nlinarith [sq_nonneg ((u - v) - (1 / 225 - 1 / 441))]
  have hn := mul_le_mul hprod hsq (sq_nonneg _) (le_of_lt (mul_pos hu hv))
  apply (le_div_iff₀ huv).mpr
  nlinarith

/-- A complete infinite-series positivity criterion, for every nonzero direction.
The finite positive nodes and every tail moment are included explicitly. -/
theorem full_hankel_two_positive {m : ℕ} (other : Fin m → ℝ)
    (hother : ∀ i, 0 ≤ other i) (u v L : ℝ)
    (hu : 0 < u) (hv : 0 < v)
    (hL : L < u * v * (u - v) ^ 2 / (u + v))
    {x y : ℕ → ℝ} (hx : ∀ n, 0 < x n)
    (h0 : Summable x)
    (h1 : Summable (fun n => x n ^ 2 - y n ^ 2))
    (h2 : Summable (fun n => x n ^ 3 - 3 * x n * y n ^ 2))
    (hloss : Summable (fun n => loss (x n) (y n)))
    (hbudget : (∑' n, loss (x n) (y n)) ≤ L) :
    ∀ a b : ℝ, (a ≠ 0 ∨ b ≠ 0) →
      0 < u * (a + b * u) ^ 2 + v * (a + b * v) ^ 2 +
        (∑ i : Fin m, other i * (a + b * other i) ^ 2) +
        (∑' n, x n) * a ^ 2 + (∑' n, (x n ^ 2 - y n ^ 2)) * (2 * a * b) +
        (∑' n, (x n ^ 3 - 3 * x n * y n ^ 2)) * b ^ 2 := by
  intro a b hab
  have htail := infinite_tail_lower hx h0 h1 h2 hloss a b
  have hscaled := mul_le_mul_of_nonneg_left hbudget (sq_nonneg b)
  have hfinite : 0 ≤ ∑ i : Fin m, other i * (a + b * other i) ^ 2 :=
    Finset.sum_nonneg (fun i _ => mul_nonneg (hother i) (sq_nonneg _))
  have hpositive := damped_two_node_positive u v L a b hu hv hL hab
  linarith

/-- The concrete HHT-004 rational budget meets the preceding theorem's hypothesis. -/
theorem concrete_budget_below_schur (u v : ℝ)
    (hu0 : 1 / 225 ≤ u) (hu1 : u ≤ 1 / 196)
    (hv0 : 1 / 484 ≤ v) (hv1 : v ≤ 1 / 441) :
    (29 / 4784677734375 : ℝ) < u * v * (u - v) ^ 2 / (u + v) := by
  have h := two_node_interval_schur u v hu0 hu1 hv0 hv1
  linarith

end HHT005

#print axioms HHT005.term_lower
#print axioms HHT005.term_summable
#print axioms HHT005.term_hasSum
#print axioms HHT005.infinite_tail_lower
#print axioms HHT005.damped_two_node_positive
#print axioms HHT005.two_node_interval_schur
#print axioms HHT005.full_hankel_two_positive
#print axioms HHT005.concrete_budget_below_schur
