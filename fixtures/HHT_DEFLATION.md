# HHT-DEFLATION: the head/nullspace bridge, its obstruction, and the correct Schur target

## Status and provenance

This extends PR15 at `6a594c0e5eb0dca8399c2867dc7e4c2f53c8b59f` without changing
its statements or overwriting the PR14 cofinal criterion. It tests the proposed
combination of the 111-node positive prefix with coefficient-balance estimates
on its nullspace. **That proposed combination does not furnish the missing
coercivity: the current coefficient certificate misses every nonzero nullspace
polynomial.** The algebraic split is nevertheless useful once its actual Schur
complement, including the mixed-term penalty, is retained.

Theorems below have written proofs and exact regressions. Kernel execution and
full CI are reported separately by the accompanying PR; no execution is inferred
from source text. No new actual-xi matrix dimension, novelty claim, independent
mathematical review, canonical Result, or RH proof is asserted.

## 1. Define the split instead of assuming an orthogonal complement

Retain the complete moments and forms

$$
F(w^2)=\xi(1/2+w)/\xi(1/2),\qquad
F'/F=\sum_{n\ge0}(-1)^n\mu_nz^n,\qquad
\mathcal B_k(p,q)=\sum_{i,j}p_iq_j\mu_{k+i+j},\quad Q_k(p)=\mathcal B_k(p,p).
$$

Let $u_1,\ldots,u_N$ be distinct certified positive real reciprocal nodes, and
put $A_N(X)=\prod_{j=1}^N(X-u_j)$. For $d=N+M$, $M\ge1$, polynomial division gives

$$
\mathbb R[X]_{<N+M}=\mathbb R[X]_{<N}\oplus A_N\mathbb R[X]_{<M},
\qquad p=r+A_Nq.
$$

The decomposition is unique: the remainder has degree below $N$, whereas a
nonzero multiple $A_Nq$ has degree at least $N$. The evaluation map on the $N$
anchors has kernel precisely $A_N\mathbb R[X]_{<M}$, by the factor theorem and
distinctness. Its weighted prefix form

$$
Q_k^{\mathrm{prefix}}(p)=\sum_{j=1}^N m_j u_j^{k+1}p(u_j)^2
$$

is strictly positive on the remainder space except at zero, but is identically
zero on the ideal. The split is **not automatically orthogonal for the complete
form**. The prefix is only semidefinite on the larger space, so it cannot be
used as an inner product defining a coercive complement there. Coefficientwise
Euclidean orthogonality is a different notion and does not remove spectral
cross terms.

## 2. The coefficient-balance certificate cannot certify this nullspace

### 2.1 A pointwise ceiling for PR15's exact rectangle bound

Normalize a nonzero polynomial as $p=\pm X^e[c+a(X)-b(X)]$, with $c>0$, and
$a,b$ coefficientwise nonnegative, as in PR15. For $0<l\le R$ write

$$
A_l=a(l),\ A_R=a(R),\ B_l=b(l),\ B=b(R),
$$

and retain the exact certified lower multiplier

$$
\mathcal L(p)=\operatorname{dist}(c,[B_l,B])^2+
\operatorname{dist}(B-c,[A_l,A_R])^2-(B-c)^2.
$$

**Pointwise-ceiling theorem.** For every $x\in[l,R]$,

$$
\boxed{\mathcal L(p)\le[c+a(x)-b(x)]^2.}
$$

Proof: let $u=a(x)\ge0$ and $v=b(x)\le B$. Monotonicity of nonnegative
coefficient evaluations places $(u,v)$ in the rectangle used by PR15. Thus

$$
\begin{aligned}
\mathcal L(p)
&\le(c-v)^2+(u-(B-c))^2-(B-c)^2\\
&=(c+u-v)^2-2u(B-v)\\
&\le(c+u-v)^2.
\end{aligned}
$$

This is an upper bound on the *certificate*, not on $Q_k(p)$. In particular,

$$
\boxed{p(x)=0\text{ at some }x\in[l,R]\quad\Longrightarrow\quad\mathcal L(p)\le0.}
$$

Factoring the lowest power does not remove a positive root. Global sign reversal
does not remove it either. A zero or negative multiplier is not evidence that
the actual form is negative. If additionally $a(x)>0$ and $b(x)<b(R)$, the
certificate is strictly negative at such a root even if the actual form is
strictly positive.

### 2.2 Application to the 111-node proposal

PR15 uses $l=1/625$ and $R=1/196$. The complete first-root bracket gives
$\gamma_1\in(14,15)$, so

$$
1/225<u_1=1/\gamma_1^2<1/196,
\qquad u_1\in[l,R].
$$

Every nonzero $p=A_{111}q$ vanishes at $u_1$. Consequently **none can receive a
strictly positive multiplier from the current coefficient-balance theorem**.
This proves that the specific bridge proposed in the preceding discussion is
not supplied by combining the two existing results. It does not invalidate
either existing result, and does not exclude stronger estimates using actual
moments, deflated coefficients, or additional arithmetic information.

The obstruction is not merely an artifact of permitting equality in ratio
monotonicity. For a root $s\in(l,R)$ and another $t\in(l,R)$, consider

$$m_n^{(\varepsilon)}=s^{n+1}+\varepsilon t^{n+1},\quad\varepsilon>0.$$

With $s\ne t$, this sequence is strictly positive and strictly log-convex, and
all ratios lie in $[l,R]$. If $p(s)=0$, then at any fixed shift

$$
\frac{Q_k^{(\varepsilon)}(p)}{m_k^{(\varepsilon)}}
=\frac{\varepsilon t^{k+1}p(t)^2}{s^{k+1}+\varepsilon t^{k+1}}\longrightarrow0.
$$

Therefore no positive uniform normalized lower margin for this polynomial can
be deduced solely from the two ratio endpoints and strict log-convexity. This
is a statement about that information class, not about fixed actual-xi moments.

### 2.3 The earlier sign-block theorem misses the same ideal

Descartes' rule of signs gives a second independent obstruction. For every
nonzero $q$ and positive $u_j$, multiplication by $X-u_j$ increases coefficient
sign variation by at least one. Therefore

$$
\boxed{\operatorname{var}(A_Nq)\ge N+\operatorname{var}(q)\ge N.}
$$

This holds with multiplicities and does not need distinctness for this particular
inequality. For the 111-node ideal the minimum is 111 sign changes. PR13's
nine-change class and PR14's late-shift 110-change class cannot contain a
nonzero member. Descartes is a classical theorem; it is not claimed as new.
The new Lean file uses Mathlib's established rule and proves the iterated
arbitrary-list statement.

## 3. The corrected bridge: a full Schur complement

In the ordered basis

$$1,X,\ldots,X^{N-1}, A_N,XA_N,\ldots,X^{M-1}A_N,$$

the complete form has real symmetric matrix

$$G_k=\begin{pmatrix}C_k&E_k\\E_k^T&D_k\end{pmatrix}.$$

If $A_N(X)=\sum_{a=0}^N A_aX^a$, the entries are exactly

$$
(C_k)_{ij}=\mu_{k+i+j},\quad
(E_k)_{is}=\sum_a A_a\mu_{k+i+s+a},\quad
(D_k)_{st}=\sum_{a,b}A_aA_b\mu_{k+s+t+a+b}.
$$

Thus $C_k=H_{N,k}$, while $D_k$ is a Hankel matrix for the *deflated* moments

$$\nu_n=\sum_{a,b}A_aA_b\mu_{n+a+b}.$$

For a complete absolutely summable spectrum the same formula reads

$$\nu_n=\sum_u m_u u^{n+1}A_N(u)^2,$$

because only finitely many coefficient sums are exchanged with the absolutely
convergent spectral sum. All known anchors vanish. Notice the ordinary square
$A_N(u)^2$, **not** $|A_N(u)|^2$; replacing it by a modulus square changes the
problem at the unknown complex nodes.

If $C_k\succ0$, define

$$\boxed{S_k=D_k-E_k^T C_k^{-1}E_k.}$$

Exact completion of the square gives, for remainder and quotient coordinates
$r,q$,

$$
Q_k(r+A_Nq)=
(r+C_k^{-1}E_kq)^TC_k(r+C_k^{-1}E_kq)+q^TS_kq.
$$

Therefore $G_k\succeq0$ iff $S_k\succeq0$; strict positive definiteness has
the analogous equivalence. This is the classical Schur-complement theorem.
The new Lean wrapper proves the PSD equivalence using **actual finite real
matrices and Matrix.PosSemidef**, invoking the fixed Mathlib theorem, not an
uninterpreted predicate.

The monic basis change has determinant one. Consequently

$$\det H_{N+M,k}=\det C_k\det S_k.$$

In particular the Schur determinant does not depend on which degree-$N$ monic
polynomial was used to form the chart. The entries may change by congruence;
it would be wrong to assert that every Schur *matrix* stays entrywise identical.
The implementation checks this invariant in exact arithmetic using several charts.

What is missing is not just positivity of the raw deflated form $D_k$: the
nonnegative Schur penalty $E_k^TC_k^{-1}E_k$ must also be dominated. A valid
all-dimension proof must control this full residual, or a genuinely equivalent
quantity, without presuming unrestricted positivity in order to estimate it.

## 4. Two exact countermodels protect against invalid propagation

Use the complete finite **signed-atomic countermodel**, not actual xi:

$$m_n=1+2^{-(n+1)}-\tfrac12 4^{-(n+1)}.$$

Its moments are positive and strictly log-convex at every index, as proved and
tested in PR15. It is not an unsigned zero spectrum.

### 4.1 Deflation does not preserve the ratio assumptions

For $A=X-1$,

$$\nu_n=\tfrac14\,2^{-(n+1)}-\tfrac9{32}\,4^{-(n+1)}.$$

All these numbers are positive, but their order-two determinants are negative.
In particular

$$
(\nu_0,\nu_1,\nu_2)=(7/128,23/512,55/2048),\qquad
\nu_0\nu_2-\nu_1^2=-9/16384.
$$

Thus PR15's adjacent-ratio monotonicity cannot simply be inherited by the
reweighted moments. Deflating both positive atoms with
$A=(X-1)(X-1/2)$ is even more explicit: every residual moment is negative.
The tests compare convolution of moments with an independent signed-atom sum.

### 4.2 Both diagonal blocks can be positive while the complete form is negative

For the algebraic chart $A=X-1/4$, the three-dimensional full matrix has blocks

$$
C=(11/8),\quad E=(7/8,13/16),\quad
D=\begin{pmatrix}19/32&37/64\\37/64&73/128\end{pmatrix}.
$$

Both $C$ and $D$ are strictly positive definite; $\det D=9/2048>0$. However

$$
S=\begin{pmatrix}13/352&43/704\\43/704&127/1408\end{pmatrix},
\qquad \boxed{\det S=-9/22528<0.}
$$

For $p=(X-1)(X-1/2)$ the coordinates are
$r=3/16$ and $q=X-5/4$, and the complete value is

$$\boxed{Q_0(p)=-9/2048.}$$

Here $1/4$ is the negative atom of this signed countermodel; this chart is an
algebraic counterexample to a block-gluing claim, not a certified positive
spectral prefix. The prefix-deflation failure in 4.1 separately removes genuinely
positive atoms. These roles are kept distinct.

## 5. Implementation and executed-test scope

`scripts/hht_deflation.py` provides exact rational polynomial arithmetic, monic
division, annihilators, full-moment deflation, block construction, positive-LDL
solves, pivoted determinant checks, and the Schur residual. It never fills in a
missing moment, infers global moment conditions from a finite list, or labels a
failed sufficient bound as an actual-xi counterexample. Inputs and intermediates
have explicit degree, matrix-dimension, shift and rational-size limits.

The 24 local regressions passed. They include 372 root-factor comparisons,
81 division identities, 81 Schur square-completion identities, annihilator and
sign-change grids, independent spectral/coefficient deflation routes, loss of
log-convexity, positive-diagonal/negative-full-form checks, chart invariance,
rank-one limiting examples, and malformed-input/budget refusal. The 111-anchor
rational test uses $1/j^2$ for $j=15,\ldots,125$; **these are not actual-xi roots**.
The actual-xi obstruction needs only the already certified first-root bracket,
not a fabricated rational approximation to its exact first 111 nodes.

The new workflow also reruns the inherited all-shift numerical prerequisite.
That recheck is not a new dimension result. The exact report is a countermodel
and algebraic regression report, not an RH certificate.

## 6. Formalization boundaries

`HHTDeflation.lean` has 14 statements covering finite coefficient evaluations,
actual polynomial evaluation, the exact rectangle's pointwise ceiling and root
barrier, monic-division identity, annihilator nonzero/evaluation properties,
arbitrary-list sign variation, the entire ideal's coefficient barrier, zero
prefix quadratic contribution, actual matrix Schur PSD equivalence, and scalar
square completion. Its runner first recompiles and audits the 17 coefficient
statements it imports, then compiles and audits these 14.

Not fully formalized here: the completeness/dimension count of the polynomial
basis, every spectral-to-moment bridge, the actual-xi analytic and FLINT inputs,
the limiting strict-logconvexity example, and the complete dimension-uniform
Schur inequality. Source inspection is never labelled kernel execution. Compiler
failure, unexpected dependencies, tool absence and resource failure must block.

## 7. Precise next obligation

For certified anchors and all target residual dimensions $M$, one must prove
positivity of $D_k-E_k^TC_k^{-1}E_k$ at suitable shifts (with $C_k\succ0$),
or replace it with a valid stronger sufficient estimate. The old coefficient
cone and bounded-sign classes provably do not establish the required nullspace
margin. Stronger deflated-moment estimates must be established from actual xi,
not inherited merely because the original moments passed low-order tests.

The proposed bridge has been audited and corrected, not turned into a claimed
unbounded-dimensional proof. It remains possible to use additional xi-specific
structure; this result identifies exactly where such structure is needed.

## Primary sources and reproducibility

Classical inputs, not claimed as new results:

- Mathlib polynomial division and `modByMonic_add_div`:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Polynomial/Div.html
- Descartes, including `succ_signVariations_le_X_sub_C_mul`:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Polynomial/RuleOfSigns.html
- Schur complement and the positive-matrix equivalence:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/PosDef.html
- The executable uses Mathlib commit `db584cd6d46c92f209a44c0f1c829460d327499d`
  and Lean 4.33.0, rather than tracking current online documentation.
- PR11 supplies the root bracket and all-shift input; PR14 and PR15 supply the
  exact existing claims being tested. All are in this repository.

```bash
timeout 40s python3 scripts/test_hht_deflation.py
timeout 40s python3 scripts/hht_deflation.py
timeout 400s python3 scripts/check_hht_deflation.py
```

The workflow imposes additional memory, CPU and output bounds. No old verifier,
axiom policy, canonical ledger, main branch, scheduled agent or paid model call
is changed by this work.
