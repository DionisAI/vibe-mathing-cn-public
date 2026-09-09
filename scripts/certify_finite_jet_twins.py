#!/usr/bin/env python3
"""Exact certificates for two synthetic infinite spectra with identical finite jets.

The algorithm certifies rational premises of the Rouche/real-sign proof in
HHT_FINITE_JET.md. It neither locates actual zeta zeros nor proves RH.
All roots have unit multiplicity; no adjustable noninteger spectral weights.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import prod
import json

MAX_DEGREE = 32
MAX_HEIGHT = 1000000
Poly = tuple[F, ...]


def integer(x: int, lo: int, hi: int) -> int:
    """Reject bool, floats and requests outside the finite execution budget."""
    if isinstance(x, bool) or not isinstance(x, int) or not lo <= x <= hi:
        raise ValueError(f'expected an integer in [{lo}, {hi}]')
    return x


def mul(a: Poly, b: Poly) -> Poly:
    """Exact convolution in ascending powers, for internal bounded polynomials."""
    if not a or not b or len(a) + len(b) - 2 > MAX_DEGREE:
        raise ValueError('polynomial degree budget exceeded')
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] += x*y
    return tuple(c)


def evaluate(p: Poly, x: F) -> F:
    """Horner evaluation; all decisions use the exact returned rational."""
    out = F(0)
    for c in reversed(p):
        out = out*x + c
    return out


def power_sums(p: Poly, count: int) -> tuple[F, ...]:
    """Newton identities for a monic root polynomial, returning s_1,...,s_count."""
    n = integer(len(p)-1, 1, MAX_DEGREE)
    integer(count, 1, n)
    if p[-1] != 1:
        raise ValueError('root polynomial must be monic')
    c = list(reversed(p))
    sums = [F(n)]
    for k in range(1, count+1):
        sums.append(-k*c[k] - sum((c[j]*sums[k-j] for j in range(1, k)), F(0)))
    return tuple(sums[1:])


def factor_coefficients(p: Poly) -> Poly:
    """Coefficients of product(1+z*u), obtained by polynomial reversal."""
    n = integer(len(p)-1, 1, MAX_DEGREE)
    if p[-1] != 1:
        raise ValueError('root polynomial must be monic')
    return tuple((-1)**j*p[n-j] for j in range(n+1))


def logarithmic_moments(f: Poly, count: int) -> tuple[F, ...]:
    """Independent recurrence F*(F'/F)=F'; mu_k=(-1)^k*[z^k](F'/F)."""
    integer(count, 1, len(f)-1)
    if f[0] != 1:
        raise ValueError('normalized factor must have constant coefficient one')
    q: list[F] = []
    for k in range(count):
        q.append((k+1)*f[k+1] - sum((f[j]*q[k-j] for j in range(1, k+1)), F(0)))
    return tuple((-1)**k*x for k, x in enumerate(q))


@dataclass(frozen=True)
class Twins:
    """Frozen rational construction; all roots are certified by analytic premises."""
    dimension: int
    prefix_height: int
    ordinates: tuple[int, ...]
    centers: tuple[F, ...]
    radius: F
    epsilon: F
    p0: Poly
    p_real: Poly
    p_nonreal: Poly
    boundary_bounds: tuple[F, ...]


def construct(dimension: int = 8, prefix_height: int = 50) -> Twins:
    """Build degree 2d root polynomials differing only in their constant term.

The last center is a double root of P0, not of either final polynomial.
Both final polynomials are simple-rooted. The sign of A at the last center
is positive because there are 2d-2 other centers, all larger than it.
"""
    d = integer(dimension, 2, MAX_DEGREE//2)
    H = integer(prefix_height, 1, MAX_HEIGHT)
    N = 2*d
    ordinates = tuple(range(H+1, H+N))
    centers = tuple(F(1, n*n) for n in ordinates)
    r = centers[-1]
    # Neighbor distances also protect against the unchanged square-spectrum tail.
    gaps = [abs(F(1, n*n)-F(1, k*k))
            for n in ordinates for k in (n-1, n+1)]
    h = min(r/8, min(gaps)/8, F(1, 16*(H+N)**3))
    mult = (1,)*(N-2)+(2,)
    bounds = tuple(h**m * prod((abs(c-v)-h)**ell
                   for j, (v, ell) in enumerate(zip(centers, mult)) if i != j)
                   for i, (c, m) in enumerate(zip(centers, mult)))
    eps = min(bounds)/4
    p: Poly = (F(1),)
    for c, m in zip(centers, mult):
        for _ in range(m):
            p = mul(p, (-c, F(1)))
    real = (p[0]-eps, *p[1:])
    nonreal = (p[0]+eps, *p[1:])
    out = Twins(d, H, ordinates, centers, h, eps, p, real, nonreal, bounds)
    verify(out)
    return out


def verify(t: Twins) -> dict:
    """Check every rational premise; fail rather than guess a root disposition."""
    if not isinstance(t, Twins):
        raise ValueError('expected a frozen Twins construction')
    d = integer(t.dimension, 2, MAX_DEGREE//2)
    H = integer(t.prefix_height, 1, MAX_HEIGHT)
    N, h, eps = 2*d, t.radius, t.epsilon
    def need(condition: bool, message: str) -> None:
        if not condition:
            raise ArithmeticError('certificate rejected: '+message)
    sequences = (t.ordinates, t.centers, t.p0, t.p_real,
                 t.p_nonreal, t.boundary_bounds)
    if any(not isinstance(seq, tuple) for seq in sequences):
        raise ValueError('certificate vectors must be tuples')
    need(tuple(map(len, sequences)) == (N-1, N-1, N+1, N+1, N+1, N-1), 'shape')
    for n in t.ordinates:
        integer(n, 2, MAX_HEIGHT+MAX_DEGREE)
    values = (h, eps, *t.centers, *t.p0, *t.p_real, *t.p_nonreal, *t.boundary_bounds)
    if any(isinstance(x, bool) or not isinstance(x, (int, F)) for x in values):
        raise ValueError('all certificate entries must be exact rationals')
    if any(max(F(x).numerator.bit_length(), F(x).denominator.bit_length()) > 16384
           for x in values):
        raise ValueError('certificate bit budget exceeded')
    cs, r = t.centers, t.centers[-1]
    need(t.ordinates == tuple(range(H+1, H+N)), 'square block ordinates')
    need(cs == tuple(F(1, n*n) for n in t.ordinates), 'square block centers')
    need(h > 0 and eps > 0, 'strict radius and perturbation')
    need(t.p_real == (t.p0[0]-eps, *t.p0[1:]), 'real perturbation binding')
    need(t.p_nonreal == (t.p0[0]+eps, *t.p0[1:]), 'nonreal perturbation binding')
    mult = (1,)*(N-2)+(2,)
    reconstructed: Poly = (F(1),)
    for c, m in zip(cs, mult):
        for _ in range(m):
            reconstructed = mul(reconstructed, (-c, F(1)))
    need(t.p0 == reconstructed, 'base factorization')
    for i, c in enumerate(cs):
        need(c-h > 0, 'positive disks')
        need(all(abs(c-v) > 2*h for j, v in enumerate(cs) if i != j), 'disjoint disks')
        B = h**mult[i] * prod((abs(c-v)-h)**mult[j] for j, v in enumerate(cs) if i != j)
        need(B == t.boundary_bounds[i] and eps < B, 'Rouche strict boundary')
        # For simple centers, both perturbed real polynomials change sign.
        if i < N-2:
            for p in (t.p_real, t.p_nonreal):
                need(evaluate(p, c-h)*evaluate(p, c+h) < 0, 'simple-root bracket')
    need(r+h < min(cs[:-1]), 'positive even-factor A on target interval')
    need(evaluate(t.p_real, r) < 0, 'central negative sign')
    need(evaluate(t.p_real, r-h) > 0 and evaluate(t.p_real, r+h) > 0, 'two positive sides')
    # Re(u)>0 and |u-r|<h imply |Im(u^(-1/2))| <= h/[2(r-h)^(3/2)].
    need(h*h < (r-h)**3, 'strict critical-strip width')
    need(r-2*h > (r+h)**2, 'positive heat trace comparison b-1>|c|')
    need(r-h > H*H*(r+h)**2, 'target height strictly above prefix')
    need(r-h > F(1, (H+N)**2), 'target height strictly below upper cutoff')
    need(cs[0]+h < F(1, H*H), 'real roots above prefix')
    # No inserted root can equal an unchanged positive inverse-square node.
    for n, c in zip(t.ordinates, cs):
        need(F(1, (n+1)**2) < c-h and c+h < F(1, (n-1)**2), 'unchanged-tail separation')
    a, b = power_sums(t.p_real, N), power_sums(t.p_nonreal, N)
    need(a[:-1] == b[:-1], 'exact first 2d-1 moment matching')
    need(b[-1]-a[-1] == -2*N*eps, 'first differing power sum')
    fa, fb = factor_coefficients(t.p_real), factor_coefficients(t.p_nonreal)
    need(fa[:-1] == fb[:-1], 'exact finite-factor jet')
    need(a == logarithmic_moments(fa, N), 'real Newton/log-derivative cross-check')
    need(b == logarithmic_moments(fb, N), 'nonreal Newton/log-derivative cross-check')
    return {'degree': N, 'matching_moments': N-1, 'identical_hankel_through_dimension': t.dimension,
            'unchanged_root_prefix_height': H, 'all_modified_roots_below_height': H+N,
            'real_polynomial_real_roots': N, 'nonreal_polynomial_real_roots': N-2,
            'nonreal_polynomial_conjugate_pairs': 1,
            'proof_basis': 'exact rational premises plus Rouche and real intermediate value theorem',
            'positive_heat_trace_premise': True,
            'actual_xi': False, 'full_analytic_lean_proof': False}


def payload(t: Twins) -> dict:
    """Serialize exact coefficients and inequalities, not numerical root guesses."""
    return {**verify(t), 'radius': str(t.radius), 'epsilon': str(t.epsilon),
            'centers': [str(x) for x in t.centers],
            'p_real_ascending': [str(x) for x in t.p_real],
            'p_nonreal_ascending': [str(x) for x in t.p_nonreal],
            'Rouche_lower_bounds': [str(x) for x in t.boundary_bounds]}


if __name__ == '__main__':
    print(json.dumps(payload(construct()), indent=2, sort_keys=True))
    print('FINITE_JET_TWINS_PASS: identical full H1..H8, opposite spectral reality; synthetic, not RH.')
