# HHT-COFINAL: four fixed witnesses, all-shift obstruction, and a smaller RH proof obligation

## Status and scope

This builds on PR13 at `7981d075cbf61dfdee66cb6a8d28b1ceef989851`.
It does not assert RH, new nonreal zeta zeros, or an unbounded family of
certified actual-xi matrix dimensions. The general statements below have a
self-contained proof. Their novelty is not established. Hermite interpolation,
geometric tail suppression and principal submatrix restriction are classical
inputs; a new equivalent formulation is not a proof of its positivity side.

The PR records actual executable outcomes, immutable revisions, and exactly
which statements have passed Lean. This file does not label unobserved jobs as
successful or promote a canonical Result.

## 1. Frozen spectral setting

Let U be a nonempty countable set of distinct nonzero complex numbers, closed
under conjugation, with positive integer multiplicities m(u)=m(conj(u)). Assume

$$
 \Re u>0\quad(u\in U),\qquad \sum_{u\in U}m(u)|u|<\infty.
$$

In particular U is bounded and has only finitely many points outside any disk
about zero. Integer multiplicities matter for this deduction: arbitrary tiny
positive weights alone would not ensure that discreteness property.

Define, for integers n,k>=0 and d>=1,

$$
 \mu_n=\sum_{u\in U}m(u)u^{n+1},\quad
 H_{d,k}=(\mu_{k+i+j})_{0\le i,j<d},\quad
 Q_k(p)=\sum_{u\in U}m(u)u^{k+1}p(u)^2.
$$

These sums converge absolutely for every fixed real polynomial p and fixed k.
Indeed U is bounded and p is bounded on a disk containing it, leaving a constant
multiple of the assumed summable mass. Conjugation makes all moments and forms
real. A polynomial of degree<d gives exactly its coefficient-vector quadratic
form in H_(d,k). The square is p(u)^2, NOT |p(u)|^2.

For actual xi retain

$$
 F(w^2)=\xi(1/2+w)/\xi(1/2),\qquad
 F'/F=\sum_{n\ge0}(-1)^n\mu_nz^n.
$$

Its upper-half-plane zero rho=beta+i*gamma maps to
u=-(rho-1/2)^(-2). All upper-half-plane zeros and their multiplicities are
included; lower-half-plane symmetry is not double-counted. The prior complete
low-height coverage, critical strip, xi symmetries, Hadamard product, and
N(t)=O(t log t) supply the hypotheses above. No assumption beta=1/2 is made for
unknown zeros. Under this correspondence, U is positive real exactly when RH
holds. These analytic identifications remain the explicitly documented external
inputs of the preceding work, not assertions proved by the new arithmetic code.

## 2. Four fixed polynomials detect a nonreal node at EVERY late shift

**Theorem.** If U contains a nonreal point, there exist four fixed real
polynomials P,R,P+R,P-R, an integer D, and an integer K such that all four have
degree<D and, for every integer k>=K, at least one has Q_k strictly negative.
The successful choice may depend on k. No irrational-angle or equidistribution
assumption is needed.

### Step A: isolate the node without truncating the object

Choose u*=x+iy with y>0; put rho=|u*|>0. Choose 0<r<rho. Let B contain every
point of U with modulus>r except u*,conj(u*). This is a finite conjugate-closed
set, including all ties in modulus and all competing nonreal pairs. Put

$$
 A(X)=\prod_{v\in B}(X-v)\in\mathbb R[X].
$$

A(u*) is nonzero. For either t=1 or t=i write t/A(u*)=c+ie and define

$$
 b=e/y,\qquad a=c-bx,\qquad p_t(X)=A(X)(a+bX).
$$

Then p_t vanishes on B and p_t(u*)=t. Set P=p_1, R=p_i. Both have real
coefficients and degree<=|B|+1, so choose D=|B|+2. They are fixed once the
spectral node and cutoff are fixed. Their values at the conjugate point are
the conjugates of their values at u*.

### Step B: control the ENTIRE tail

Let S=sum_(|u|<=r) m(u)|u|, and choose M bounding each of
|P|, |R|, |P+R| and |P-R| on the whole complex disk |z|<=r.
For instance the maximum of the four absolute-coefficient bounds suffices.
For every one of these four polynomials,

$$
 |Q_{\mathrm{tail},k}(p)|\le S M^2r^k.
$$

No remaining zero is discarded. Multiplicities are included. Normalize each
full form by the positive number m(u*) rho^(k+1) and define

$$
 E_k=\frac{SM^2}{m(u_*)\rho}\left(\frac r\rho\right)^k.
$$

As r/rho<1, there is a finite K such that E_k<1 for every k>=K.

### Step C: four directions cover every phase

Write u*^(k+1)/rho^(k+1)=c_k+i s_k, so c_k^2+s_k^2=1. The normalized
contributions of the target pair in the four directions are exactly

$$
 2c_k,\quad -2c_k,\quad -4s_k,\quad 4s_k.
$$

Each normalized full form is no larger than its displayed contribution plus
E_k. If all four full forms were nonnegative with E_k<1, we would have
|c_k|<1/2 and |s_k|<1/4. This contradicts c_k^2+s_k^2=1.
Thus at least one is strictly negative at every k>=K. This proves the theorem.

This handles rational phases, roots of unity and arbitrarily small nonzero
imaginary parts alike. The threshold may grow when separation is poor. A single
fixed polynomial is NOT claimed to be negative at every shift.

## 3. The stronger consequence: a uniform dimension obstruction at ALL shifts

A shifted Hankel block is an actual principal submatrix:

$$
 H_{D,k+2M}=H_{D+M,k}[M:M+D,\ M:M+D].
$$

Take M=ceil(K/2). Since k+2M>=K for every k>=0, the preceding theorem implies

$$
 \boxed{H_{d,k}\not\succeq0
 \quad\text{for every }d\ge D+\lceil K/2\rceil,\quad\text{every }k\ge0.}
$$

Equivalently use the four fixed polynomials X^M P, X^M R, X^M(P+R),
X^M(P-R): Q_k(X^M p)=Q_(k+2M)(p). Thus a nonreal node imposes a finite cap
on positive-semidefinite block sizes, uniformly over every possible shift.
This is not an assertion about the smallest failing dimension.

**Dimension-cofinal criterion.** Under Section1's assumptions,

$$
 \boxed{
 U\subset(0,\infty)
 \quad\Longleftrightarrow\quad
 \forall D\ge1\ \exists d\ge D\ \exists k\ge0:
 H_{d,k}\succeq0.}
$$

Proof: with all nodes positive real, every form is a sum of nonnegative terms,
so every block is PSD. Conversely a nonreal node gives the uniform dimension
cap just proved, contradicting the right side. If U has infinite distinct
support, the positive-real case is strictly positive on every nonzero
polynomial, so PSD may be replaced by positive definiteness in that setting.
With finite support only the PSD formulation is generally correct.

For actual xi this is an RH-equivalent target. Successful shifts may vary
arbitrarily with dimension; they do not have to grow or cover all shifts.
It is enough to certify positive blocks at an unbounded sequence of sizes.
**We have not established such an unbounded actual-xi sequence.** A generic
threshold-existence theorem conditional on positive real anchors does not
supply infinitely many complete positive-real prefixes for free.

## 4. Exact infinite-spectrum regression

The complete synthetic reciprocal spectrum is

$$
 U=\{1/n^2:n\ge1\}\cup\{u_*,\bar u_*\},\qquad
 u_*=\frac{18480+1088i}{1338649}
       =\left(\frac{17}{2}-\frac i4\right)^{-2}.
$$

All multiplicities are one. Its norm rho=16/1157 is rational. Take
B={1,1/4,...,1/64}, r=1/81, and S=1/8. The last inequality covers the entire
n>=9 tail by integral comparison, not by enumerating a finite number of terms.
The implementation constructs P and R of degree nine by the formulas above,
with A=product_(n=1)^8 (X-1/n^2). Uniform disk bounds use the absolute
coefficients, hence are valid on a complex disk, not merely on the real axis.

Exact rational computation gives

$$
 \alpha=r/\rho=1157/1296,\qquad E_{207}<1.
$$

The computed upper bound is approximately 0.8936167555269072; the decision
uses a rational upper endpoint, not this display. Direct exact exponentiation
also checks that the dyadic power enclosure is outward for this certificate.
Therefore

$$
 H_{10,k}\not\succeq0\quad(k\ge207),\qquad
 H_{114,k}\not\succeq0\quad(k\ge0).
$$

Only four fixed polynomial directions are needed in each claim; their choice
can switch with k. The executable prints the exact P,R coefficients, cutoff,
full-tail mass and threshold. Selected phase samples are extra regressions,
not a proof of the infinite range. This is NOT an actual-xi counterexample.

## 5. Positive side: use all 111 certified low-height actual-xi nodes

The numerical executable `certify_xi_cofinal.py` attempts a bounded concrete
application on the other side of the criterion. It reuses the complete
full-strip counting below height256, requires N(256)=111 and all counted cells
to be singletons, and checks strict separation of all111 inverse-node intervals.
It uses the previous analytic bounds r=1/65536 and S=7/128 for ALL unknown
zeros above256, without assuming they lie on the critical line.

For distinct positive anchors u_j and deg(p)<d, the prior interpolation argument
bounds the full relative tail by sum_j c_j alpha_j^k. Here the exact arithmetic
uses the conservative aggregate

$$
 C=d\max_jc_j,\quad \alpha=\max_j\alpha_j<1,\qquad
 \sum_jc_j\alpha_j^k\le C\alpha^k.
$$

Lagrange basis bounds are on the entire complex tail disk. If C*alpha^K<1,
then every H_(d,k), k>=K, is positive definite; lower dimensions are principal
blocks. The executable attempts d=10,20,40,80,111 at two pinned precisions.
Actual thresholds and successful execution are recorded in the PR only after
observing the numerical job. No small-shift positivity at those new orders is
asserted; the existing d<=10 all-shift result is left unchanged.

Threshold search uses binary exponentiation with directed dyadic multiplication:
replace each positive product by its ceiling on a fixed dyadic grid. Induction
on the arithmetic expression proves an upper bound at every operation. Thus
roundoff can reject an otherwise valid threshold but cannot manufacture one.
A finite resource limit yielding no threshold means inconclusive. These
bounds do not compute an approximate eigenvalue of an ill-conditioned
111-square matrix and call that a certificate.

This is a finite number of certified dimensions, NOT the unbounded-dimensional
hypothesis in Section3. Even a large numerical threshold is not an estimate
uniform in dimension.

## 6. Formal verification and executable boundaries

`HHTCofinal.lean` contains the phase norm invariant, the four-direction
inequality, upper envelopes for actual infinite sums, existence of a geometric
threshold, and negativity at every sufficiently late shift. It also defines
actual finite Hankel matrices and proves their principal-submatrix shift
identity, the all-shift uniform dimension obstruction, and the dimension-cofinal
contradiction using Matrix.PosSemidef. This is not merely an uninterpreted
Boolean positivity predicate.

The spectral construction of the isolating real polynomials, the conversion
of spectral moments to the finite quadratic form, and actual-xi analytic/FLINT
inputs are not fully formalized here. The polynomial interpolation part is a
self-contained prose proof plus exact rational executable specialization.
Accordingly no end-to-end actual-xi Lean proof is claimed.

The runner requires the existing fixed Lean4.33.0/Mathlib revision and permits
only the established dependency set. Missing tools, failed compilation,
unapproved dependencies and absent audit records block the job. No old verifier
or axiom policy is changed. Numeric routines reject floats, booleans, repeated
anchors, overlapping intervals, absent strict spectral gap, non-unit phases,
invalid multiplicities where applicable, and exceeded budgets.

```bash
(ulimit -v 524288; ulimit -t 20; timeout 30s python3 scripts/test_hht_cofinal.py)
(ulimit -v 2097152; ulimit -t 300; timeout 300s python3 scripts/certify_xi_cofinal.py)
timeout 300s python3 scripts/check_hht_cofinal.py
```

Full execution prints interval and rational certificates. `--summary` omits
large inputs and supplies a digest, not a substitute for recomputing the evidence.
No scheduled job, paid model call, new credential, main-branch change or
canonical Result is introduced.

## 7. Attribution and remaining mathematical work

Hermite-Sylvester interpolation is classical. A modern self-contained reference
is M. Nathanson, *The Hermite-Sylvester criterion for real-rooted polynomials*,
arXiv:1911.01745v1. It supplies historical/methodological context, not the
infinite-tail or cofinal theorem as an asserted quotation:
https://arxiv.org/html/1911.01745v1

The geometric limit and PSD submatrix APIs were checked against primary
Mathlib sources. Compilation uses the repository's pinned revision, not a
moving documentation build:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/SpecificLimits/Basic.html
https://github.com/leanprover-community/mathlib4/blob/db584cd6d46c92f209a44c0f1c829460d327499d/Mathlib/LinearAlgebra/Matrix/PosDef.lean

Actual-xi full counting, normalization and the analytic tail mass input are
in `HHT_SHIFTS.md`, `XI_STRIP.md`, and PR11. The optional TP/sign-change
corollary for the newly certified late-shift range follows exactly as in PR12
and PR13; it does not remove the new range's lower shift threshold.

The next research target is a source-based estimate yielding positive blocks
at unbounded dimensions, with one chosen shift per dimension now sufficient.
The first111 counted real nodes supply a finite benchmark only. Infinitely
many known critical-line zeros by themselves cannot be substituted for complete
positive-real prefixes: unknown intervening nodes must remain in the tail bound.
