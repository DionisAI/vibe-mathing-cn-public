# HHT coefficient balance: the previously uncovered amplitude regime

## Status and provenance

Based on PR14 commit `2a85fd7c8fd311c4a161b01f1c216e0c86eeab3b`.
PR14's cofinal criterion and order111 work are preserved. This also brings the
previously delivered but unpublished coefficient-cone source into the repository.
Actual execution is reported by the accompanying PR and immutable workflow logs;
source text, finite tests, numerical enclosures and Lean compilation are distinct.
No canonical Result, novelty claim, independent-review claim or RH proof is made.

## 1. Frozen definitions and a general finite-polynomial theorem

Use complete actual-xi moments, not a finite zero product:

$$F(w^2)=\xi(1/2+w)/\xi(1/2),\qquad
F'/F=\sum_{n\ge0}(-1)^n\mu_nz^n,\qquad
Q_k(p)=\sum_{i,j}c_ic_j\mu_{k+i+j}.$$

The generic theorem applies to any strictly positive sequence m whose adjacent
ratios are nondecreasing and lie in [l,R], with 0<l<=R. Given a nonzero finite
real polynomial, remove its lowest power and its overall sign:

$$p(X)=\pm X^e(c+a(X)-b(X)),\qquad c>0.$$

a,b have nonnegative coefficients and no constant term. Their supports are the
coefficients respectively agreeing and disagreeing with the lowest coefficient.
Set t=k+2e, A_l=a(l), A_R=a(R), B_l=b(l), B=b(R). For a real number z and interval
[L,U], let d(z,[L,U]) denote its ordinary distance to the closed interval.

**New bound, including B>c:**

$$\boxed{Q_k(p)\ge m_t\mathcal L(p),}$$

$$\boxed{\mathcal L(p)=d(c,[B_l,B])^2+
 d(B-c,[A_l,A_R])^2-(B-c)^2.}$$

If L(p)>0, this proves strict positivity for every shift. If L(p)=0 it proves
only nonnegativity; if L(p)<0 the certificate is inconclusive, not a negative
witness. There is no mathematical restriction on polynomial degree, term count,
sign changes, or coefficient size. The execution budgets are separate.

This extends, rather than discards, the preceding theorem:

$$B\le c\ \Longrightarrow\ Q_k(p)\ge m_t(c-B)^2.$$

The new lower multiplier is at least (c-B)^2 whenever B<=c. It can also be
strictly positive when B>c, the regime explicitly left uncovered before.

## 2. Proof: retain both self-terms and bound the mixed term

Nondecreasing adjacent ratios give, for every t,i,j>=0,

$$m_tm_{t+i+j}\ge m_{t+i}m_{t+j}.$$

The upper and lower ratio bounds give

$$l^j m_{t+i}\le m_{t+i+j}\le R^j m_{t+i}.$$

These identities follow by finite products of adjacent ratios; no higher-order
positive definiteness is assumed. Normalize the two linear evaluations:

$$u=\frac{\sum_i a_i m_{t+i}}{m_t},\qquad
v=\frac{\sum_j b_j m_{t+j}}{m_t}.$$

Then u belongs to [A_l,A_R] and v belongs to [B_l,B]. Rank-one entry lower
bounds and nonnegative a_i,b_j imply

$$Q_t(a)/m_t\ge u^2,\qquad Q_t(b)/m_t\ge v^2.$$

Separately the mixed form E=sum a_i b_j m_(t+i+j) satisfies E/m_t<=Bu. Thus

$$\begin{aligned}
Q_t(c+a-b)/m_t
&\ge c^2+u^2+v^2+2cu-2cv-2Bu\\
&=(c-v)^2+(u-(B-c))^2-(B-c)^2.
\end{aligned}$$

The expression separates into two squared distances. Its minimum on the stated
rectangle is exactly L(p), proving the claim. The rectangle may contain (u,v)
pairs no actual sequence realizes, so this is a sufficient lower bound, not a
characterization of all positive directions.

For B<=c, B-c<=0<=A_l and v<=B<=c, whence L(p)>=(c-B)^2. For B>c,
a useful explicit sufficient condition is A_l>=2(B-c):

$$Q_k(p)\ge m_t A_l[A_l-2(B-c)].$$

Indeed f(u)=u[u-2(B-c)] is increasing on u>=A_l>=2(B-c), and (c-v)^2>=0.
The final value is strictly positive when A_l>2(B-c). Cross terms have not
been thrown away or estimated with an assumed all-degree Cauchy inequality.

## 3. Application to actual xi, with two global ratio bounds

The analytic inputs remain precisely those documented in PR11: positivity and
strict log-convexity at every shift, the complete low-height zero cover, and
absolutely convergent Hadamard moments including unknown off-line zeros.
For rho=beta+i gamma let delta=beta-1/2 and u=(gamma-i delta)^(-2).
The complete root cover excludes gamma<=14, so |u|<1/196=R. If
C=sum m_u |u|<infinity, then 0<mu_n<=C R^n. An increasing adjacent ratio cannot
exceed R: any ratio r>R would give mu_(n+j)>=mu_n r^j, contradicting this
geometric upper bound. This argument does not assume unknown roots are on-line.

The new numerical runner separately checks the initial ratio satisfies

$$\mu_1/\mu_0>1/625=:l.$$

Together with all-index ratio monotonicity this gives the global lower bound.
This is a finite new interval computation plus a mathematical propagation
argument, not extrapolation from a ratio plot. The dedicated workflow reruns
PR11's complete all-shift numerical prerequisites before checking new examples.

## 4. A whole family excluded by the previous amplitude condition

For every positive integer N, put Y=196X and

$$p_N(X)=1+8Y+\sum_{j=2}^N Y^{2j-1}
                -\frac2N\sum_{j=1}^N Y^{2j}.$$

The polynomial has degree 2N, 2N+1 nonzero terms, and 2N-1 sign changes.
Here c=1, B=2, so the old B<=c condition fails for every N. But

$$A_l\ge8\cdot196/625=1568/625>2,$$

and hence

$$\boxed{Q_k(p_N)\ge\frac{498624}{390625}\,\mu_k>0
\quad(N\ge1,\ k\ge0).}$$

This covers, for example, N=25: 51 terms and 49 sign changes, failing both the
old nine-sign-change criterion and the old amplitude criterion. It does not
cover all polynomials and does not supply an unbounded family of whole positive
Hankel matrices required by PR14's cofinal target.

## 5. Anti-circularity and finite regression obligations

The tests deliberately include the indefinite signed-atomic moment sequence

$$m_n=1+2^{-(n+1)}-\tfrac12 4^{-(n+1)}.$$

It is strictly positive, bounded and strictly log-convex. Its initial ratio is
39/44 and its upper ratio bound is 1. For every k>=0,

$$m_km_{k+2}-m_{k+1}^2\ge(13/128)2^{-(k+1)}>0.$$

Yet q(X)=(X-1)(X-1/2) has Q_0(q)=-9/2048. The new rectangular certificate is
negative for that polynomial and reports **inconclusive**. An explicit finite
signed-atomic calculation independently checks the actual negative value.
At a rank-one equality boundary the form can be zero, so a zero multiplier
is never relabelled strict. Widening the allowed ratio interval cannot improve
the lower bound and is tested. Global negation, coefficient scaling, factoring
X^e, zero coefficients, malformed inputs and resource exhaustion are tested.

The 22 earlier coefficient tests are retained. Twelve new tests include 625
coefficient patterns at three shifts on the indefinite model, exact rectangle
minima, the rescued family, unchanged negative witnesses, and interval monotonicity.
These are finite regressions, not a substitute for the general proof.

## 6. Numerical and Lean scope

`certify_xi_balance.py` recomputes 108 complete actual-xi moments at 2048 and
3072 bits in pinned python-flint 0.8.0. It verifies the initial ratio and N=5,25
at shifts 0,7 by both direct double sums and squared-coefficient convolution.
Every example must exceed the stated rational rectangle bound with a strictly
positive interval margin. Positive scaling is explicitly 196^(k+1)Q_k(p).
No zero locations are input to this coefficient computation. Two precisions
are repeated executions of one backend, not independent implementations.
The full report includes all moment and result endpoints; --summary does not.

`HHTCoefficientCone.lean` contains seventeen statements: ten pending finite
cone/ratio statements from the previous delivery plus seven new statements for
squared distance, normalized two-self-term lower bounds, rectangle minimization,
arbitrary finite-kernel assembly, rescue by positive mass, lower-ratio propagation,
and the exact universal-family multiplier. The finite kernel dimension is
arbitrary. The pointwise kernel assumptions are explicit, not global axioms.

Unformalized connections: the actual-xi/FLINT analytic inputs, the global
spectral-growth-to-ratio argument, telescoping monotone ratios to the all-gap
rank-one inequality, and the complete polynomial-to-coordinate bridge. The
new Lean file does not itself define xi. Actual compiler success and each
approved dependency audit are required before its statements are called checked.
The existing verifier and dependency policy are unchanged. Outcomes are recorded
by the accompanying PR; no outcome is inferred from this source document.

## 7. Reproduction and remaining obligation

```bash
timeout 40s python3 scripts/test_hht_coefficient_cone.py
timeout 40s python3 scripts/test_hht_balance.py
timeout 300s python3 scripts/certify_xi_balance.py
timeout 300s python3 scripts/check_hht_coefficient_cone.py
```

The workflow supplies additional CPU/memory/output bounds. The local portable
arithmetic has no network or external solver. No scheduled job, paid model call,
new credential, canonical admission or automatic merge is introduced.

The unresolved region is not merely B>c anymore: it is the directions for which
all available sufficient lower bounds fail. A negative rectangle bound does
not imply Q is negative. Establishing a dimension-uniform actual-xi estimate
or unbounded successful whole-matrix dimensions remains an independent task.

## Primary sources and attribution

The finite inequalities are proved above; no novelty claim is made.
Classical xi definition/symmetry: https://dlmf.nist.gov/25.4
Critical-strip background: https://dlmf.nist.gov/25.10
Frozen actual-xi all-shift inputs: PR11 in this repository, commit
`0d348524e4ea126e37105a51a7adf2fcd2ea17cc`.
Finite-sum APIs (actual compilation uses the pinned Mathlib revision):
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/BigOperators/Ring/Finset.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Order/BigOperators/Group/Finset.html
