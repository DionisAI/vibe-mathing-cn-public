#!/usr/bin/env python3
"""Bounded exact arithmetic for four-direction eventual Hankel obstructions.

Rational spectral inputs are explicit hypotheses, not certified actual-xi zeros.
No network, subprocess, model invocation or canonical ledger writes.
"""
from __future__ import annotations
from fractions import Fraction as F

MAX_PREFIX = 128
MAX_ORDER = 8192
MAX_BITS = 131072
MAX_THRESHOLD = 10000000


def rat(x):
    """Require bounded exact arithmetic, excluding booleans and approximate numbers."""
    if type(x) not in (int, F):
        raise ValueError('exact rational required')
    x = F(x)
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ValueError('input bit budget exceeded')
    return x


def pair(z):
    """Validate a Gaussian-rational pair."""
    if not isinstance(z, (list, tuple)) or len(z) != 2:
        raise ValueError('two rational coordinates required')
    return rat(z[0]), rat(z[1])


def add(z, w):
    return z[0]+w[0], z[1]+w[1]


def mul(z, w):
    return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]


def inv(z):
    z = pair(z); den = z[0]**2+z[1]**2
    if not den:
        raise ValueError('zero complex divisor')
    return z[0]/den, -z[1]/den


def cpow(z, n):
    """Bounded exact complex power by squaring."""
    z = pair(z)
    if type(n) is not int or not 0 <= n <= MAX_ORDER:
        raise ValueError('exponent budget exceeded')
    cost = max(max(v.numerator.bit_length(), v.denominator.bit_length()) for v in z)*max(n,1)
    if cost > MAX_BITS:
        raise ValueError('power bit budget exceeded')
    out = F(1), F(0)
    while n:
        if n & 1:
            out = mul(out, z)
        n >>= 1
        if n:
            z = mul(z, z)
    return out


def poly_mul(p, q):
    if not p or not q or len(p)+len(q)-1 > MAX_PREFIX+2:
        raise ValueError('polynomial size budget exceeded')
    out = [F(0)]*(len(p)+len(q)-1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i+j] += rat(a)*rat(b)
    return out


def poly_eval(p, z):
    """Horner evaluation on a Gaussian rational, not a floating root finder."""
    z = pair(z)
    out = F(0), F(0)
    for a in reversed(p):
        out = add(mul(out, z), (rat(a), F(0)))
    return out


def phase_basis(anchors, target):
    """Two real polynomials vanishing at anchors, taking values 1 and i at target.

    This executable specialization uses positive real anchors. The proof allows
    a finite conjugate-closed prefix with nonreal anchors as well.
    """
    if not isinstance(anchors, (list, tuple)) or len(anchors) > MAX_PREFIX:
        raise ValueError('anchor budget exceeded')
    nodes = list(map(rat, anchors)); x, y = pair(target)
    if y == 0 or x <= 0 or any(a <= 0 for a in nodes) or len(set(nodes)) != len(nodes):
        raise ValueError('positive distinct anchors and nonreal right-half-plane target required')
    A = [F(1)]
    for u in nodes:
        A = poly_mul(A, [-u, F(1)])
    denom = inv(poly_eval(A, (x, y)))
    out = []
    for t in ((F(1), F(0)), (F(0), F(1))):
        re, im = mul(t, denom)
        b = im/y; a = re-b*x
        out.append(poly_mul(A, [a, b]))
    return out


def four_polynomials(P, R):
    if len(P) != len(R):
        raise ValueError('basis lengths differ')
    return [list(P), list(R), [a+b for a,b in zip(P,R)], [a-b for a,b in zip(P,R)]]


def circle_bound(p, radius):
    """Uniform bound on the entire complex disk from absolute coefficients."""
    r = rat(radius)
    if r < 0 or not p or len(p) > MAX_PREFIX+2:
        raise ValueError('invalid disk or polynomial')
    return sum((abs(rat(a))*r**j for j,a in enumerate(p)), F(0))


def pow_upper(a, n, bits):
    """Directed dyadic upper bound for a^n; no huge rational exponent expansion."""
    a = rat(a)
    if not 0 <= a <= 1 or type(n) is not int or not 0 <= n <= MAX_THRESHOLD:
        raise ValueError('invalid contracting power')
    if type(bits) is not int or not 32 <= bits <= 16384:
        raise ValueError('precision budget exceeded')
    scale = 1 << bits
    q = -((-a.numerator*scale)//a.denominator)
    value = scale
    while n:
        if n & 1:
            value = (value*q+scale-1)//scale
        n >>= 1
        if n:
            q = (q*q+scale-1)//scale
    return F(value, scale)


def threshold(C, a, maximum=MAX_THRESHOLD):
    """A sufficient K with C*a^K<1; exhaustion means inconclusive, never false."""
    C, a = rat(C), rat(a)
    if C < 0 or not 0 <= a < 1 or type(maximum) is not int or not 0 <= maximum <= MAX_THRESHOLD:
        raise ValueError('invalid threshold problem')
    bits = max(128, C.numerator.bit_length()-C.denominator.bit_length()+96)
    if bits > 16384:
        raise ValueError('precision budget exhausted')
    def bound(k):
        return C*pow_upper(a,k,bits)
    if C < 1:
        return {'K':0,'upper':C,'bits':bits}
    high = 1
    while high < maximum and not bound(high) < 1:
        high = min(2*high, maximum)
    if high > maximum or not bound(high) < 1:
        return None
    low = 0
    while high-low > 1:
        mid = (low+high)//2
        if bound(mid) < 1:
            high = mid
        else:
            low = mid
    return {'K':high,'upper':bound(high),'bits':bits}


def phase_candidates(z):
    """Normalized contributions of P,R,P+R,P-R for one unit complex phase."""
    x,y = pair(z)
    if x*x+y*y != 1:
        raise ValueError('phase must have exact unit norm')
    return [2*x,-2*x,-4*y,4*y]


def synthetic_certificate():
    """Complete infinite square spectrum plus one nonreal pair; not actual xi."""
    target = F(18480,1338649), F(1088,1338649)
    rho = F(16,1157); radius = F(1,81); mass = F(1,8)
    if target[0]**2+target[1]**2 != rho*rho or not radius < rho:
        raise ArithmeticError('spectral normalization error')
    anchors = [F(1,n*n) for n in range(1,9)]
    P,R = phase_basis(anchors,target); polys = four_polynomials(P,R)
    M = max(circle_bound(p,radius) for p in polys)
    C = mass*M*M/rho; alpha = radius/rho
    result = threshold(C,alpha,maximum=4096)
    if result is None:
        raise ArithmeticError('negative-witness budget inconclusive')
    K = result['K']
    # Independent exact-power check for this bounded synthetic certificate.
    if not C*alpha**K <= result['upper'] < 1:
        raise ArithmeticError('directed-power certificate invalid')
    phase = (target[0]/rho,target[1]/rho)
    samples = []
    for k in [K,K+1,K+2,K+3,K+17,K+64]:
        vals = phase_candidates(cpow(phase,k+1)); chosen = min(range(4),key=vals.__getitem__)
        error = C*alpha**k
        if not vals[chosen]+error < 0:
            raise ArithmeticError('phase obstruction lost strictness')
        samples.append({'k':k,'choice':chosen,'normalized_upper':str(vals[chosen]+error)})
    return {'target':[str(t) for t in target],'modulus':str(rho),
        'tail_radius':str(radius),'complete_tail_mass_upper':str(mass),
        'P':[str(a) for a in P],'R':[str(a) for a in R], 'dimension':len(P),
        'disk_majorant':str(M),'C':str(C),'alpha':str(alpha),
        'K':K,'budget_upper':str(result['upper']),
        'budget_display':float(result['upper']),'samples':samples,
        'statement':'H_(10,k) has a negative direction for EVERY integer k>=K',
        'which_direction_may_depend_on_k':True,'actual_xi_counterexample':False}


def positive_prefix_envelope(intervals, radius, mass):
    """C*alpha^k dominates the full Lagrange relative-tail envelope.

    Conditional on complete, distinct, positive real anchors and the supplied
    full-tail radius and mass; this routine alone does not verify root inputs.
    """
    if not isinstance(intervals,(list,tuple)) or not 1 <= len(intervals) <= MAX_PREFIX:
        raise ValueError('prefix size budget exceeded')
    r,S = rat(radius),rat(mass)
    if r <= 0 or S < 0:
        raise ValueError('invalid radius or mass')
    boxes = [pair(v) for v in intervals]
    if any(not r < a <= b for a,b in boxes):
        raise ValueError('missing strict spectral gap')
    C = F(0); alpha = F(0)
    for j,(lo,hi) in enumerate(boxes):
        M = F(1)
        for i,(a,b) in enumerate(boxes):
            if i == j:
                continue
            gap = max(lo-b,a-hi)
            if gap <= 0:
                raise ValueError('anchor intervals overlap or touch')
            M *= (r+b)/gap
        C = max(C,S*M*M/lo)
        alpha = max(alpha,r/lo)
    return len(boxes)*C,alpha
