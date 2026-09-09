#!/usr/bin/env python3
"""Exact polynomial localization of a conjugate pair in a summable spectrum.

Inverse nodes u=1/lambda are Gaussian rationals. General certificates are
conditional on the declared COMPLETE head and tail radius/mass bounds.
The square-spectrum fixture has a proved tail envelope; see HHT_LOCALIZATION.md.
No network, subprocess, float sign decisions, or canonical ledger writes.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

Q = int | F
Z = tuple[F, F]
MAX_BITS = 64
MAX_HEAD = 16
MAX_POWER = 256


def rational(value: Q) -> F:
    """Keep caller inputs exact, non-boolean and within the bit budget."""
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError('expected int or Fraction')
    value = F(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise ValueError('input bit budget exceeded')
    return value


def integer(value: int, lo: int, hi: int) -> int:
    """Reject implicit bools, floats and out-of-budget iteration counts."""
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ValueError(f'expected integer in [{lo}, {hi}]')
    return value


def node(value: tuple[Q, Q]) -> Z:
    """Parse a nonzero Gaussian-rational inverse node."""
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError('expected (real, imaginary)')
    z = rational(value[0]), rational(value[1])
    if z == (0, 0):
        raise ValueError('zero is a limit point, not an allowed spectral node')
    return z


def mul(z: Z, w: Z) -> Z:
    """Multiply exact complex pairs; internal values can exceed input bit bounds."""
    return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]


def inv(z: Z) -> Z:
    """Invert a nonzero exact complex pair."""
    s = z[0]*z[0]+z[1]*z[1]
    if not s:
        raise ValueError('division by zero')
    return z[0]/s, -z[1]/s


def power(z: Z, n: int) -> Z:
    """Bounded repeated squaring; zero powers have the usual value one."""
    n = integer(n, 0, MAX_POWER)
    out = F(1), F(0)
    while n:
        if n & 1:
            out = mul(out, z)
        z = mul(z, z)
        n >>= 1
    return out


def evaluate(coefficients: tuple[F, ...], z: Z) -> Z:
    """Horner evaluation of an ascending-order real polynomial."""
    out = F(0), F(0)
    for c in reversed(coefficients):
        out = mul(out, z)
        out = out[0]+c, out[1]
    return out


def annihilator(nodes: tuple[Z, ...]) -> tuple[F, ...]:
    """Multiply X-u factors, checking that the result has real coefficients."""
    coeffs = [(F(1), F(0))]
    for z in nodes:
        new = [(F(0), F(0)) for _ in range(len(coeffs)+1)]
        for j, c in enumerate(coeffs):
            cz = mul(c, z)
            new[j] = new[j][0]-cz[0], new[j][1]-cz[1]
            new[j+1] = new[j+1][0]+c[0], new[j+1][1]+c[1]
        coeffs = new
    if any(c[1] for c in coeffs):
        raise ValueError('head is not conjugate closed')
    return tuple(c[0] for c in coeffs)


def first_power(C: Q, theta: Q, eta: Q, budget: int = MAX_POWER) -> tuple[int, F]:
    """Find C*theta^M<eta exactly; exhaustion is inconclusive, never a sign claim.

C may be a derived rational larger than the input bit budget.
"""
    if any(isinstance(v, bool) or not isinstance(v, (int, F)) for v in (C, theta, eta)):
        raise ValueError('power search needs exact rational arguments')
    C, theta, eta = F(C), F(theta), F(eta)
    budget = integer(budget, 0, MAX_POWER)
    if C < 0 or not 0 <= theta < 1 or eta <= 0:
        raise ValueError('need C>=0, 0<=theta<1, eta>0')
    if max(max(v.numerator.bit_length(), v.denominator.bit_length())
           for v in (C, theta, eta)) > 16384:
        raise ValueError('derived constant bit budget exceeded')
    value = C
    for M in range(budget+1):
        if value < eta:
            return M, value
        value *= theta
    raise ArithmeticError('INCONCLUSIVE: power budget exhausted')


@dataclass(frozen=True)
class Localization:
    """A structural contract, NOT a proof that the supplied head is complete."""
    target: tuple[Q, Q]
    head: tuple[tuple[Q, Q], ...]
    tail_radius: Q
    tail_mass: Q
    multiplicity: int = 1

    def __post_init__(self) -> None:
        """Require real symmetry, a genuine complex target, and a strict gap."""
        z = node(self.target)
        if z[0] <= 0 or z[1] <= 0:
            raise ValueError('target must have positive real and imaginary parts')
        if not isinstance(self.head, (list, tuple)) or len(self.head) > MAX_HEAD:
            raise ValueError('head budget exceeded')
        head = tuple(node(v) for v in self.head)
        if len(set(head)) != len(head):
            raise ValueError('use distinct head nodes; multiplicities do not add factors')
        if z in head or (z[0], -z[1]) in head:
            raise ValueError('head cannot contain either target node')
        if any((a, -b) not in head for a, b in head):
            raise ValueError('head must be conjugate closed')
        r, S = rational(self.tail_radius), rational(self.tail_mass)
        m = integer(self.multiplicity, 1, 1024)
        if r <= 0 or S < 0 or r*r >= z[0]*z[0]+z[1]*z[1]:
            raise ValueError('need positive radius, nonnegative mass, strict spectral gap')
        object.__setattr__(self, 'target', z)
        object.__setattr__(self, 'head', head)
        object.__setattr__(self, 'tail_radius', r)
        object.__setattr__(self, 'tail_mass', S)
        object.__setattr__(self, 'multiplicity', m)

    def constants(self) -> dict[str, F]:
        """Compute a rational C, theta, eta with Q(p_M)<=-eta+C*theta^M."""
        z, r, S = self.target, self.tail_radius, self.tail_mass
        A = annihilator(self.head)
        Az = evaluate(A, z)
        A2 = Az[0]*Az[0]+Az[1]*Az[1]
        if A2 == 0:
            raise ValueError('annihilator must not vanish at the target')
        boundA = sum((abs(c)*r**j for j, c in enumerate(A)), F(0))
        kappa = 1 + (abs(z[0])+r)/abs(z[1])
        theta = r*r/(z[0]*z[0]+z[1]*z[1])
        return {'C': S*boundA**2*kappa**2/A2, 'theta': theta,
                'eta': 2*self.multiplicity*z[0], 'A_bound': boundA}

    def witness(self, M: int) -> dict:
        """Construct p_M with p_M(target)=i, killing every declared head node."""
        M = integer(M, 0, MAX_POWER)
        A = annihilator(self.head)
        z, r = self.target, self.tail_radius
        w = mul((F(0), F(1)), inv(mul(power(z, M), evaluate(A, z))))
        b = w[1]/z[1]
        a = w[0]-b*z[0]
        p = [F(0)]*(M+len(A)+1)
        for j, c in enumerate(A):
            p[M+j] += a*c
            p[M+j+1] += b*c
        while len(p) > 1 and p[-1] == 0:
            p.pop()
        p = tuple(p)
        if evaluate(p, z) != (0, 1):
            raise ArithmeticError('target normalization invariant failed')
        if any(evaluate(p, u) != (0, 0) for u in self.head):
            raise ArithmeticError('head annihilation invariant failed')
        c = self.constants()
        geometric = c['C']*c['theta']**M
        direct = self.tail_mass*r**(2*M)*c['A_bound']**2*(abs(a)+r*abs(b))**2
        if direct > geometric:
            raise ArithmeticError('derived majorant invariant failed')
        upper = -c['eta']+direct
        return {'power': M, 'degree': len(p)-1, 'dimension': len(p),
                'coefficients': p, 'a': a, 'b': b, **c,
                'geometric_tail_bound': geometric, 'direct_tail_bound': direct,
                'full_upper': upper,
                'decision': 'negative_under_stated_bounds' if upper < 0 else 'inconclusive',
                'tail_premises_verified_by_structure': False}

    def find_witness(self, budget: int = MAX_POWER) -> dict:
        """Bounded search justified by geometric contraction, not by sample signs."""
        c = self.constants()
        M, _ = first_power(c['C'], c['theta'], c['eta'], budget)
        return self.witness(M)


def square_spectrum(gamma: Q = F(3, 2), delta: Q = F(1, 4)) -> Localization:
    """Spectrum: lambda_n=n^2 and (gamma±i*delta)^2, not actual xi zeros.

For N=floor(gamma), head n=1..N; remaining inverse nodes <=1/(N+1)^2
and their total mass <=1/N by a telescoping majorant. All premises are
proved for this explicitly defined synthetic spectrum in HHT_LOCALIZATION.md.
"""
    g, d = rational(gamma), rational(delta)
    N = g.numerator//g.denominator
    integer(N, 1, MAX_HEAD)
    if not 0 < d <= F(1, 2) or g <= N or g*g+d*d >= (N+1)**2:
        raise ValueError('need N<gamma, 0<delta<=1/2 and gamma^2+delta^2<(N+1)^2')
    target = inv((g*g-d*d, -2*g*d))
    return Localization(target, tuple((F(1, n*n), F(0)) for n in range(1, N+1)),
                        F(1, (N+1)**2), F(1, N))


def real_square_partial(p: tuple[F, ...], start: int, stop: int) -> F:
    """A bounded finite sanity sum; NEVER used as the infinite-tail certificate."""
    start = integer(start, 1, 128)
    stop = integer(stop, start, 128)
    if not isinstance(p, tuple) or not 1 <= len(p) <= MAX_HEAD+MAX_POWER+2:
        raise ValueError('invalid polynomial size')
    return sum((F(1, n*n)*evaluate(p, (F(1, n*n), F(0)))[0]**2
                for n in range(start, stop+1)), F(0))


if __name__ == '__main__':
    for g in (F(3, 2), F(5, 2), F(9, 2), F(17, 2)):
        cert = square_spectrum(g).find_witness()
        print(f'gamma={g}, power={cert["power"]}, dimension={cert["dimension"]}, '
              f'negative={cert["full_upper"] < 0}; exact infinite-tail bound, synthetic only')
