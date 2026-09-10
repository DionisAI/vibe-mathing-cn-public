# HHT-TOTAL: sparse-polynomial positivity and the next dimension boundary

## Status and frozen dependency

This is a research fixture, not a canonical Result or an RH proof. The new
mathematical conclusion below is a corollary of the actual-xi all-shift result
in PR #11, commit `0d348524e4ea126e37105a51a7adf2fcd2ea17cc`, and a classical
strict total-positivity theorem. Neither Fekete's theorem nor its use here is
claimed as a new general theorem. Source novelty has not been established.

The associated PR #12 records execution outcomes and immutable code revisions.
Verification is split between exact arithmetic, strict ball computation and
kernel-checked statements. Neither finite experiments nor source inspection
are treated as verification of unbounded mathematical quantifiers.

## 1. Definitions and hypotheses

Retain the normalization

$$
 F(w^2)=\xi(1/2+w)/\xi(1/2),\qquad
 F'(z)/F(z)=\sum_{n\ge0}(-1)^n\mu_nz^n.
$$

Write $H_{d,k}=(\mu_{k+i+j})_{0\le i,j<d}$ and
$\tau_d(k)=\det H_{d,k}$, with $\tau_0(k)=1$.
The frozen PR #11 result establishes $H_{d,k}\succ0$ for every integer
$1\le d\le10$ and every integer $k\ge0$. Its trust boundary includes FLINT
ball special functions and full-strip counting, classical xi symmetries and
Hadamard correspondence, and the documented analytic zero-count estimate.
This note neither changes nor silently removes those inputs.

For increasing nonnegative integer lists $I=(i_1,\ldots,i_s)$ and
$J=(j_1,\ldots,j_s)$ define

$$
 D_{I,J,k}=\det(\mu_{k+i_a+j_b})_{1\le a,b\le s}.
$$

The two index lists need not be consecutive, equal, or bounded in magnitude.
They must be kept in increasing order: reversing one changes determinant signs.

## 2. Actual-xi corollary: every minor of order at most ten

For every $1\le s\le10$, every pair of strictly increasing nonnegative integer
lists $I,J$ of length $s$, and every integer $k\ge0$,

$$
 \boxed{D_{I,J,k}>0.}
$$

This says the infinite shifted Hankel matrix is *strictly totally positive of
order ten*. It does not say that all minors of every order are positive.

### Proof

Fix $I,J,k$ and embed the target in a finite rectangle of
$A=(\mu_{k+i+j})_{i,j\ge0}$. Every contiguous square submatrix of order
$t\le10$ is $H_{t,k+a+b}$ for suitable nonnegative $a,b$, and has positive
determinant by PR #11. Lemma 2.4 of [FJS] therefore gives positivity of all
minors of order at most ten in that finite rectangle, including the target.
The argument applies separately to every finite choice of indices. There is
no limiting determinant and no extrapolation from the numerical examples.

For completeness, the classical finite-minor mechanism can be organized in
two passes. A rectangle with at most ten consecutive columns has all its solid
minors positive, so the finite Fekete theorem makes it totally positive. Next,
restrict the original matrix to any at most ten selected rows. Its solid minors
lie in the just-certified consecutive-column rectangles. Applying the finite
Fekete theorem to this selected-row matrix certifies the arbitrary target.
The finite Fekete theorem itself remains a cited input, not a new Lean theorem.

Strictness is essential in this general-matrix argument. The three-cycle
permutation matrix has nonnegative contiguous minors but a negative
noncontiguous two-by-two minor. This rejection example is in the tests.

## 3. Removing the degree cap, not the support-size cap

Let

$$
 p(X)=\sum_{a=1}^{s}c_aX^{e_a},\qquad
 0\le e_1<\cdots<e_s,\quad 1\le s\le10,
$$

where the real coefficient vector is nonzero. For every integer $k\ge0$,

$$
 \boxed{Q_k(p)=\sum_{a,b=1}^{s}c_ac_b\mu_{k+e_a+e_b}>0.}
$$

Indeed, the selected symmetric matrix has all leading principal minors
positive by Section 2, hence is positive definite by Sylvester's criterion.
There is *no upper bound on the exponents*. In particular the conclusion applies
to a polynomial with ten terms and largest exponent one million just as it does
to a degree-nine polynomial. The numerical examples do not attempt to evaluate
coefficients of that magnitude; the theorem, not enumeration, covers them.

Under the established xi moment correspondence, this is also the full zero-sum
quadratic form, including multiplicities. For each fixed finite-degree $p$,
absolute convergence follows from $\sum m_u|u|<\infty$ and bounded reciprocal
nodes: $|u^{k+1}p(u)^2|\le R^k\max_{|z|\le R}|p(z)|^2|u|$.
A zero polynomial gives zero and is explicitly excluded from strictness.

**Search consequence.** Any actual-xi negative polynomial certificate, at any
nonnegative shift, must have at least eleven nonzero coefficients in the
ordinary monomial basis. This is a lower bound, not existence of such a
certificate, and is basis-dependent. It is not a claim that degree eleven
suffices, nor an impossibility statement about all approaches to RH.

## 4. The exact dimension-lifting obligation

Desnanot-Jacobi condensation gives, for $d\ge1$,

$$
 \boxed{\tau_{d+1}(k)\tau_{d-1}(k+2)
 =\tau_d(k)\tau_d(k+2)-\tau_d(k+1)^2.}
$$

When the middle $(d-1)$-square block is invertible, this follows immediately
by taking its Schur complement in the $(d+1)$-square block: its two diagonal
Schur entries produce the two principal bordered determinants, its off-diagonal
entry produces the mixed bordered determinant, and the full determinant is the
two-by-two Schur determinant times the middle determinant. The possible sign
of the mixed bordered determinant disappears on squaring. Polynomial continuity
extends the identity to singular matrices. The $d=1$ case is the ordinary
two-by-two determinant with the empty determinant equal to one.

In our positive preceding-order setting no singular extension is needed. For
$1\le d\le9$, PR #11 makes both factors on the left strictly positive, hence

$$
 \tau_d(k+1)^2<\tau_d(k)\tau_d(k+2)\quad\text{for every }k\ge0.
$$

Thus every determinant sequence through order nine is strictly log-convex and
its adjacent ratios increase. At order ten the precise *next* obligation is

$$
 \boxed{\forall k\ge0:\quad
 \tau_{10}(k+1)^2<\tau_{10}(k)\tau_{10}(k+2).}
$$

Because $\tau_9(k+2)>0$, this is equivalent to positivity of $\tau_{11}(k)$ at
every shift, and hence, using the already-positive lower leading minors, to
$H_{11,k}\succ0$ for every shift. It is a reformulation, **not an independent
proof** of the missing inequality. Even proving this one next order would not
by itself establish a bound uniform over all orders.

A finite obstruction to treating positivity of a determinant row as enough is
$\mu=(1,2,5,14,40)$. Its three contiguous two-by-two determinants are $(1,3,4)$,
and in fact every minor of size at most two of the three-square Hankel matrix
is positive. Nevertheless its full determinant is $-1$, since
$1\cdot4-3^2=-5=(-1)\cdot5$.

## 5. Implementation, finite computation and formal coverage

`hht_total_math.py` implements bounded exact selected minors, LU sign checks,
sparse quadratic forms and direct checks of the five-determinant condensation
identity. An LU certificate of positive leading minors of a nonsymmetric matrix
is **not** labelled a positive-definite quadratic form. The routine checks that
index order, shift, matrix sizes and exact rational inputs are valid. Integer
LU inputs are converted to Fraction before division; approximate or mixed
arithmetic is rejected, and the numerical path accepts finite FLINT arb only. Unknown
ball pivots fail closed. Enumeration routines are finite regression oracles,
not a checker of an infinite total-positivity claim.

`certify_xi_sparse.py` recomputes actual xi coefficients, with no zero locations
or finite zero product as input. It attempts four gapped minors at 2048 and
3072 bits, including the ten-term support

```
0, 1, 3, 6, 10, 15, 21, 28, 36, 45
```

at shifts zero and seven. A nonsymmetric cross-minor is separately labelled.
The script also attempts the order-ten log-convexity defect at shifts zero
through four, checking it against the independently computed product
$\tau_{11}(k)\tau_9(k+2)$. These five finite successes, if observed, do **not**
settle every shift at order eleven. Positive row/column rescaling uses
$a_n=200^{n+1}\mu_n$; condensation remains exact because both sides have the
same scaling exponent.

`HHTTotal.lean` contains eleven statements. Actual kernel execution is a
separate job with the existing toolchain and axiom-dependency policy:

- Adjacent strict log-convexity gives increasing ratios; arbitrary positive
  exponent gaps give positive order-two minors. This genuinely quantifies
  unbounded natural exponents and shifts.
- A real two-by-two square completion gives all nonzero two-term directions.
- The exact condensation identity, supplied explicitly, yields the equivalence
  of the entire next determinant row with strict log-convexity of the preceding
  row; it does not assert the needed xi inequality.
- The $(1,2,5,14,40)$ next-order obstruction is checked arithmetically.

**Not newly formalized:** the full Fekete theorem at order ten, general
Desnanot-Jacobi determinants, Sylvester's full finite-dimensional criterion,
xi special functions/zero counts, or RH. The prose TP10 and ten-term corollaries
use their cited classical inputs and the frozen PR11 computational result.
The general recurrence in Lean is a local premise, not a new global postulate.

## 6. Reproduction and next concrete question

Run at the repository root, with pinned python-flint 0.8.0 where required:

```bash
(ulimit -v 524288; ulimit -t 20; timeout 30s python3 scripts/test_hht_total.py)
(ulimit -v 2097152; ulimit -t 300; timeout 300s python3 scripts/certify_xi_sparse.py)
timeout 300s python3 scripts/check_hht_total.py
```

The numerical executable defaults to full interval evidence; `--summary`
prints a compact execution record and the full-report digest. The compact
record is not a replacement for the interval evidence when independently
rechecking the numbers. The dedicated workflow also recomputes the PR11 all-shift numerical prerequisite.
No scheduled agents, paid model calls, new secrets or canonical ledger writes
are introduced. Existing checks are not weakened. Main and other research
branches are unchanged.

The next mathematical target is an actual-xi estimate for
$\tau_{d}(k)\tau_{d}(k+2)-\tau_{d}(k+1)^2$ that remains positive as the order grows.
This note isolates that obligation and excludes monomial-sparse negative search
through ten terms; it does not claim the growing-order estimate has been found.

## Sources and attribution

[FJS] S. Fallat, C. R. Johnson, A. D. Sokal, *Total positivity of sums, Hadamard
products and Hadamard powers: Results and counterexamples*, Linear Algebra and
its Applications 520 (2017), 242–259; arXiv:1612.02210v2 includes the 2021
corrigendum. Section 2.1, Theorem 2.2 and Lemma 2.4 supply the strict
contiguous-minor criterion. The correction to the nonnegative Hankel discussion
is not used to weaken strictness here. Checked 2026-09-09.
https://arxiv.org/html/1612.02210v2

The all-gap order-two proof is written independently using monotone ratios.
The determinant condensation identity and Sylvester's criterion are classical
linear algebra; our quotient and exact tests do not claim their discovery.
Mathlib's natural-number strict-monotonicity API was checked against the
primary documentation, while compilation uses the repository's fixed revision.
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/Monotone/Basic.html

PR11 and its mathematical input references:
https://github.com/DionisAI/vibe-mathing-cn-public/pull/11
