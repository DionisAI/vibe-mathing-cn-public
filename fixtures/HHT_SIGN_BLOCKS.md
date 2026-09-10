# HHT-SIGN-BLOCKS: dense polynomial positivity from ordered compression

## Frozen scope and status

This research fixture builds on PR #12, commit
`348afe2bee10a09864ae38e96438edc312046c07`. It changes neither the canonical
ledger nor any existing trust verifier. Strict TP10 of the actual xi moment
kernel is a frozen input, with precisely PR12/PR11's numerical and classical
analytic dependencies. No novelty claim or RH proof is made.

The accompanying PR records actual execution and immutable code revisions.
A written proof, a finite regression, a ball-arithmetic certificate, and a Lean
compilation are separately reported. An unwitnessed execution is not a PASS.

## 1. New conclusion: replace the term bound by a sign-change bound

Keep

$$
 F(w^2)=\xi(1/2+w)/\xi(1/2),\qquad
 F'(z)/F(z)=\sum_{n\ge0}(-1)^n\mu_nz^n.
$$

For a nonzero real polynomial $p(X)=\sum_{a=1}^n c_a X^{e_a}$ with strictly
increasing nonnegative integer exponents and nonzero coefficients, let $v(p)$
be the number of sign changes in $(c_1,\ldots,c_n)$. Zero coefficients are
removed before counting; reversing the entire sequence does not change the
count. Define

$$
 Q_k(p)=\sum_{a,b=1}^n c_ac_b\mu_{k+e_a+e_b},\qquad k\in\mathbb N.
$$

**Actual-xi corollary.** For every such $p$ with $v(p)\le9$ and every $k\ge0$,

$$
 \boxed{Q_k(p)>0.}
$$

There is **no bound on the degree or the number of nonzero coefficients**.
The polynomial is finite, however; this does not assert positivity for arbitrary
infinite power series without convergence arguments. In particular, a polynomial
with a million nonzero coefficients but only two sign changes is covered.
The zero polynomial is excluded because its form is zero.

This strictly enlarges PR12's ten-term class. A prospective actual-xi negative
polynomial direction must have **at least ten sign changes**, and hence at least
eleven nonzero monomials, in this particular coefficient basis. This is a
necessary condition, not existence of a negative direction or a sufficient
condition for negativity. Do not confuse coefficient sign changes with real
root counts: no assertion of ten positive real roots follows here.

## 2. General finite theorem and self-contained proof

Let $A=(K(e_i,e_j))$ be a real symmetric kernel restriction and suppose every
minor of order at most $r$, with increasing row and column indices, is strictly
positive. A finite coefficient vector $c\ne0$ has $s$ same-sign runs, $s\le r$.
Write their nonempty index sets as

$$
 B_1<B_2<\cdots<B_s,
$$

meaning every index in an earlier set is less than every index in a later set.
Within a block put $w_i=|c_i|>0$ and let $\sigma_a\in\{1,-1\}$ be its sign.
Form the $s\times s$ matrix

$$
 C_{ab}=\sum_{i\in B_a}\sum_{j\in B_b}w_iw_jA_{ij}.
$$

### The determinant expansion

Choose any $t$ increasing block-row indices $a_1<\cdots<a_t$ and block-column
indices $b_1<\cdots<b_t$. Multilinearity in rows and then columns gives

$$
 \det(C_{a_\alpha b_\beta})_{\alpha,\beta=1}^t
 =\sum_{i_\alpha\in B_{a_\alpha}}\sum_{j_\beta\in B_{b_\beta}}
 \left(\prod_{\alpha=1}^t w_{i_\alpha}\right)
 \left(\prod_{\beta=1}^t w_{j_\beta}\right)
 \det(A_{i_\alpha j_\beta})_{\alpha,\beta=1}^t.
$$

There are no factorial factors: one independently chooses exactly one original
row per block-row and one original column per block-column. Because blocks are
ordered, both resulting index lists are strictly increasing. Every selected
minor is therefore positive, every weight product is positive, and the finite
sum has at least one term. Thus **every minor of $C$ is strictly positive**.
Symmetry of $A$ gives symmetry of $C$. All leading principal minors of $C$ are
positive, so Sylvester's criterion makes $C$ positive definite. Finally,

$$
 c^T A c=\sigma^T C\sigma>0.
$$

The whole sign vector is nonzero. This proves the finite theorem for arbitrary
finite block sizes. More generally, any positive weighted mixing on ordered
disjoint row/column supports preserves strict total positivity through the
available order. Alternation of the block signs is used only to identify the
minimal number of blocks for a given direction, not in the compression identity.

### Application to xi and the complete infinite spectrum

For fixed $k$ take $A_{ij}=\mu_{k+e_i+e_j}$. PR12 proves strict total positivity
through order ten for arbitrary index gaps and every nonnegative shift. With
$s=v(p)+1\le10$, the finite theorem applies. It uses the *complete actual xi*
moments, not moments of a finite zero product. Under the previously documented
Hadamard correspondence, the equivalent spectral series includes every unknown
zero and multiplicity. For each fixed polynomial it is absolutely convergent:
bounded reciprocal nodes and $\sum m_u|u|<\infty$ bound
$|u^{k+1}p(u)^2|$ by a constant times $|u|$.

## 3. Why the ordering hypothesis cannot be dropped

Consider

$$
 A=\begin{pmatrix}1&2&5\\2&5&14\\5&14&40\end{pmatrix},\qquad
 c=(3,-4,1)^T.
$$

All minors of $A$ through order two are strictly positive, yet $c^TAc=-1$.
The vector has two sign changes, not at most one. Grouping all positive entries
into one block $\{0,2\}$ and all negative entries into another $\{1\}$ would
incorrectly claim only two blocks. The supports interlace, and the resulting
compressed matrix is

$$
 C=\begin{pmatrix}79&80\\80&80\end{pmatrix},\qquad \det C=-80.
$$

It is not covered by the ordered theorem. The test suite rejects interlaced,
overlapping, repeated and out-of-order index selections rather than accepting
these as a valid proof certificate. Globally changing all signs does not change
$Q$ or the number of sign changes; inserting zero coefficients changes neither.

## 4. Bounded implementation and actual-xi experiment

`hht_sign_blocks.py` implements exact sign-run extraction, ordered positive
compression, a separate determinant expansion oracle, direct quadratic forms,
and a *conditional* direction classifier. The classifier explicitly reports
`kernel_input_verified_here=false`: classifying signs does not verify the
analytic xi input. Too many sign changes returns uncovered, not negative.
Exact inputs are int/Fraction only; booleans, floats, invalid indices, zero
weights, overlapping supports and exhausted enumeration budgets are rejected.
All finite budgets are engineering limits, not theorem quantifier limits.

`test_hht_sign_blocks.py` has 20 finite regressions, including independent
multilinear expansions, all minors of a compressed Cauchy matrix, ordered versus
interlaced supports, sparse and dense directions, exponent gaps, invalid data
and exact arithmetic. These checks do not prove universal quantifiers.

`certify_xi_sign_blocks.py` recomputes 106 complete actual-xi moments, without
using zero locations, independently at 2048 and 3072 bits of the same pinned
python-flint 0.8.0 backend. It attempts the dense degree-49 polynomial

$$
 p(X)=\sum_{i=0}^{49}(-1)^{\lfloor i/5\rfloor}200^i X^i.
$$

This has **50 nonzero terms and nine sign changes**. The blocks are
$\{0,\ldots,4\},\{5,\ldots,9\},\ldots,\{45,\ldots,49\}$.
At shifts zero and seven the program computes all ten compressed Schur/LU
pivots and the original direction by two finite organizations of the sums.
Scaling $a_n=200^{n+1}\mu_n$ makes the matrix
$C_{ab}=200^{k+1}L_k(b_a b_b)$ where $b_a=\sum_{i\in B_a}200^iX^i$.
The positive scalar does not change the sign. No interval is silently rounded
to zero or converted into a floating-point sign decision. All pivots and both
direction enclosures must be strictly positive; uncertainty fails closed.

The dedicated job first reruns PR11's full all-shift numerical prerequisite.
The two dense examples cross-check the corollary; its unbounded term counts and
exponents are supplied by the proof, not extrapolated from those examples.
The executable defaults to full interval evidence; `--summary` carries a digest
but is not a replacement for the full interval record.

## 5. Lean statement fidelity

`HHTSignBlocks.lean` contains ten statements. The accompanying bounded
runner must actually compile them with the existing fixed Lean/Mathlib versions
and audit every printed dependency before a kernel PASS can be reported.

The formal core proves row expansion, column expansion, weight extraction,
**the full double determinant expansion**, its strict positivity for nonempty
finite positive supports, the strict ordering of arbitrary selected indices,
and strict positivity of the genuinely compressed determinant. It also proves
symmetry, exact quadratic regrouping and the finite alternating boundary.
Block cardinalities and finite matrix order are not bounded by execution examples.

The selected-minor assumption is a precisely stated local hypothesis on $K$;
positivity of the *already-compressed* matrix is not assumed to prove itself.
Choosing any leading subcollection gives its positive determinant, as in the
prose proof. The general Fekete theorem, Sylvester's criterion, the sign-run
parser's full connection to arbitrary polynomial syntax, and the actual-xi
analytic/FLINT inputs are not newly formalized in this file. Consequently this
is not an end-to-end Lean proof about the zeta function or RH. The permitted
dependency policy and all previous verifiers are unchanged.

## 6. Remaining mathematical obligation

The result replaces a support-size bound by a sign-variation bound, and hence
covers some genuinely dense directions in every dimension. It still leaves
polynomials with ten or more coefficient sign changes uncontrolled. We have
not derived a recurrence that preserves the needed determinant log-convexity
as the order grows. A sum of positive low-sign-change quadratic directions
does not automatically control cross terms, so splitting an arbitrary vector
into such pieces is not a proof of unrestricted positivity.

Next useful target: derive a xi-specific bound on interactions between ordered
sign blocks that remains valid as the number of blocks increases, or find a
rigorously certified negative direction within that remaining class. Merely
changing basis to reduce sign changes is invalid unless positivity of the
transformed kernel is independently established. This research fixture makes
neither the existence of a negative xi direction nor RH a conclusion.

## Sources and reproduction

Strict TP10 is PR12's frozen actual-xi corollary, based on the strict Fekete
criterion in Fallat, Johnson and Sokal, *Total positivity of sums, Hadamard
products and Hadamard powers: Results and counterexamples*, Lemma 2.4:
https://arxiv.org/html/1612.02210v2
The ordered compression argument above is a direct multilinearity/Cauchy-Binet
consequence, not a claimed new general theorem or a substitute for novelty review.

Lean API references (the executable uses the repository's pinned revision):
https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/Determinant/Basic.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Multilinear/Basic.html

```bash
(ulimit -v 524288; ulimit -t 20; timeout 30s python3 scripts/test_hht_sign_blocks.py)
(ulimit -v 2097152; ulimit -t 300; timeout 300s python3 scripts/certify_xi_sign_blocks.py)
timeout 300s python3 scripts/check_hht_sign_blocks.py
```

Jobs are bounded and read-only; there are no scheduled agents, new credentials,
paid model calls, canonical admissions or automatic merges. Actual execution
outcomes belong to the accompanying PR and its immutable Actions runs.
