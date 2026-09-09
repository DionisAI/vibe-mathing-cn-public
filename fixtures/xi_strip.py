#!/usr/bin/env python3
"""HHT-004: exact xi-coordinate geometry and conditional height-tail bounds.

These functions do not locate zeta zeros or certify completeness of root boxes.
Analytic inputs and the k=0 restriction are stated in XI_STRIP.md.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F

MAX_BITS = 128
MAX_DEGREE = 12
MAX_NODES = 128
MAX_POWER = 80


def rat(x: int | F) -> F:
    """Accept bounded exact rationals; reject bool, floats and other coercions."""
    if isinstance(x, bool) or not isinstance(x, (int, F)):
        raise ValueError("expected int or Fraction")
    x = F(x)
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ValueError("input exceeds bit budget")
    return x


def natural(n: int, lo: int, hi: int) -> int:
    """Validate a finite integer loop bound without accepting a boolean."""
    if isinstance(n, bool) or not isinstance(n, int) or not lo <= n <= hi:
        raise ValueError("integer outside fixture budget")
    return n


def poly(p: list[int | F] | tuple[int | F, ...]) -> tuple[F, ...]:
    """Read a nonzero polynomial in ascending coefficient order."""
    if not isinstance(p, (list, tuple)) or not 1 <= len(p) <= MAX_DEGREE + 1:
        raise ValueError("invalid polynomial degree")
    values = tuple(rat(x) for x in p)
    if not any(values):
        raise ValueError("zero polynomial is not a sign witness")
    return values


@dataclass(frozen=True)
class Interval:
    """Closed rational enclosure; arithmetic does not assert root membership."""
    lo: F
    hi: F

    def __post_init__(self) -> None:
        """Keep endpoints exact and ordered; internal arithmetic may grow in bits."""
        if any(isinstance(v, bool) or not isinstance(v, (int, F)) for v in (self.lo, self.hi)):
            raise ValueError("interval endpoints must be exact rationals")
        object.__setattr__(self, "lo", F(self.lo))
        object.__setattr__(self, "hi", F(self.hi))
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    def __add__(self, other: Interval) -> Interval:
        """Outward-exact interval addition."""
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __neg__(self) -> Interval:
        """Reflect an interval about zero."""
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other: Interval) -> Interval:
        """Outward-exact subtraction."""
        return self + (-other)

    def __mul__(self, other: Interval) -> Interval:
        """Enclose all four endpoint products without rounding."""
        v = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval(min(v), max(v))

    def square(self) -> Interval:
        """Square with explicit handling of a zero-crossing interval."""
        return Interval(F(0) if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2),
                        max(self.lo**2, self.hi**2))

    def reciprocal(self) -> Interval:
        """Reject inversion if zero belongs to the enclosure."""
        if self.lo <= 0 <= self.hi:
            raise ValueError("cannot invert an interval containing zero")
        return Interval(1 / self.hi, 1 / self.lo)


def point(x: int | F) -> Interval:
    """Embed an exact scalar as a degenerate interval."""
    return Interval(F(x), F(x))


def lambda_coordinates(beta: int | F, gamma: int | F) -> tuple[F, F]:
    """Map ONE upper-half-plane rho to lambda=-(rho-1/2)^2; no zero claim."""
    beta, gamma = rat(beta), rat(gamma)
    if not 0 <= beta <= 1 or gamma <= 0:
        raise ValueError("expected upper-half-plane coordinates in the closed strip")
    d = beta - F(1, 2)
    return gamma**2 - d**2, -2 * gamma * d


def _log_unit_interval(y: F, terms: int) -> Interval:
    """Enclose log(y), 1<=y<=2, by the atanh series and its positive tail."""
    z = (y - 1) / (y + 1)
    value = 2 * sum((z**(2*j+1) / (2*j+1) for j in range(terms)), F(0))
    remainder = 2 * z**(2*terms+1) / ((2*terms+1) * (1-z*z))
    return Interval(value, value + remainder)


def log_interval(x: int | F, terms: int = 16) -> Interval:
    """Rational enclosure for log(x), x>=1; binary range reduction is exact."""
    x = rat(x)
    natural(terms, 1, 32)
    if x < 1:
        raise ValueError("log enclosure is restricted to x>=1")
    exponent = 0
    while x >= 2:
        x /= 2
        exponent += 1
    return point(exponent) * _log_unit_interval(F(2), terms) + _log_unit_interval(x, terms)


def height_power_bound(T: int | F, power: int) -> F:
    """Bound sum_{gamma>T} m*gamma^-power under N(t)<=t*log(t), t>=50.

The global counting theorem is an external analytic dependency, not a
software-verified property of any user-supplied list. All upper zeros count.
"""
    T = rat(T)
    natural(power, 2, MAX_POWER)
    if T < 50:
        raise ValueError("the selected counting corollary is only used for T>=50")
    gap = power - 1
    return power * T**(1-power) * (log_interval(T).hi / gap + F(1, gap*gap))


def absolute_quadratic_tail(p: list[int | F] | tuple[int | F, ...],
                            k: int, T: int | F) -> F:
    """Two-sided absolute tail bound with a HEIGHT cutoff, not a modulus cutoff."""
    values = poly(p)
    natural(k, 0, 12)
    return sum((abs(a*b) * height_power_bound(T, 2*(k+i+j+1))
                for i, a in enumerate(values) if a
                for j, b in enumerate(values) if b), F(0))


def negative_quadratic_tail(p: list[int | F] | tuple[int | F, ...], T: int | F) -> F:
    """Only for k=0: Q_tail(p)>=-returned_bound; NOT an absolute-value bound.

Uses the full critical strip |beta-1/2|<=1/2, paired conjugacy, and the
counting theorem. It needs no assertion that tail zeros lie on the line.
"""
    values, T = poly(p), rat(T)
    if T < 50:
        raise ValueError("height cutoff must be at least 50")
    factor = 1 / (1 - F(1, 4) / T**2)
    return factor * sum((i*j*abs(a*b) * height_power_bound(T, 2*i+2*j+4)
                         for i, a in enumerate(values) if i and a
                         for j, b in enumerate(values) if j and b), F(0))


def negative_matrix_tail(d: int, T: int | F) -> F:
    """For k=0, H_tail>=-E*diag(0,1,...,1); constant direction has no loss."""
    natural(d, 1, MAX_DEGREE + 1)
    T = rat(T)
    if T < 50:
        raise ValueError("height cutoff must be at least 50")
    factor = 1 / (1 - F(1, 4) / T**2)
    return factor * sum((j*j * height_power_bound(T, 4*j+4) for j in range(1, d)), F(0))


def point_unshifted_term(beta: int | F, gamma: int | F,
                         p: list[int | F] | tuple[int | F, ...]) -> F:
    """Re[u*p(u)^2] at one rational strip point, not a computed zeta zero."""
    a, b = lambda_coordinates(beta, gamma)
    norm2 = a*a + b*b
    x, y = a/norm2, -b/norm2
    P, Q = F(0), F(0)
    for c in reversed(poly(p)):
        P, Q = P*x-Q*y+c, P*y+Q*x
    return x*(P*P-Q*Q)-2*y*P*Q


@dataclass(frozen=True)
class RootBox:
    """A proposed zero rectangle; existence, multiplicity and coverage are NOT proved."""
    beta_lo: int | F
    beta_hi: int | F
    gamma_lo: int | F
    gamma_hi: int | F
    multiplicity: int = 1

    def __post_init__(self) -> None:
        """Validate only geometry and an upper-half-plane counting convention."""
        for name in ("beta_lo", "beta_hi", "gamma_lo", "gamma_hi"):
            object.__setattr__(self, name, rat(getattr(self, name)))
        natural(self.multiplicity, 1, 1024)
        if not (0 <= self.beta_lo <= self.beta_hi <= 1
                and 0 < self.gamma_lo <= self.gamma_hi):
            raise ValueError("invalid upper-strip rectangle")

    def reflected_key(self) -> tuple[F, F, F, F, int]:
        """Reflect rho to 1-conj(rho), which conjugates the lambda node."""
        return (1-self.beta_hi, 1-self.beta_lo, self.gamma_lo,
                self.gamma_hi, self.multiplicity)

    def key(self) -> tuple[F, F, F, F, int]:
        """Canonical exact rectangle identity for duplicate and symmetry checks."""
        return (self.beta_lo, self.beta_hi, self.gamma_lo, self.gamma_hi, self.multiplicity)

    def inverse_lambda(self) -> tuple[Interval, Interval]:
        """Enclose u=1/lambda=(gamma+i*delta)^2/(gamma^2+delta^2)^2."""
        g = Interval(self.gamma_lo, self.gamma_hi)
        d = Interval(self.beta_lo-F(1, 2), self.beta_hi-F(1, 2))
        denominator = (g.square()+d.square()).square().reciprocal()
        return (g.square()-d.square())*denominator, point(2)*g*d*denominator


def prefix_structure(boxes: list[RootBox], T: int | F) -> dict[str, int | bool | str]:
    """Reject duplicate/overlapping/unpaired boxes; NEVER certify actual zero coverage."""
    T = rat(T)
    if not isinstance(boxes, list) or not 1 <= len(boxes) <= MAX_NODES:
        raise ValueError("empty or oversized proposed prefix")
    if not all(isinstance(b, RootBox) and b.gamma_hi <= T for b in boxes):
        raise ValueError("invalid box or a box crosses the height cutoff")
    keys = {b.key() for b in boxes}
    if len(keys) != len(boxes):
        raise ValueError("duplicate boxes would double-count zeros")
    if any(b.reflected_key() not in keys for b in boxes):
        raise ValueError("upper-strip reflection or multiplicity is missing")
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            if (max(a.beta_lo, b.beta_lo) <= min(a.beta_hi, b.beta_hi)
                    and max(a.gamma_lo, b.gamma_lo) <= min(a.gamma_hi, b.gamma_hi)):
                raise ValueError("overlapping closed boxes can double-count a zero")
    return {"supplied_multiplicity": sum(b.multiplicity for b in boxes),
            "cutoff_kind": "height", "actual_zeros_verified": False,
            "completeness_verified": False}


def conditional_prefix_interval(boxes: list[RootBox], p: list[int | F] | tuple[int | F, ...],
                                T: int | F) -> Interval:
    """Enclose k=0 prefix IF the boxes really enclose exactly the claimed zero multiset."""
    prefix_structure(boxes, T)
    values = poly(p)
    result = point(0)
    for box in boxes:
        x, y = box.inverse_lambda()
        P, Q = point(0), point(0)
        for coefficient in reversed(values):
            P, Q = P*x-Q*y+point(coefficient), P*y+Q*x
        term = x*(P.square()-Q.square())-point(2)*y*P*Q
        result = result + point(box.multiplicity)*term
    return result


def coarse_h2_comparison() -> dict[str, F | str]:
    """Conditional two-root Schur margin; log(50)<4 is proved in the prose.

Premises not checked here: one line zero in each of (14,15),(21,22), and all
other prefix zeros below 50 on the line. No real-zero certification is emitted.
"""
    umin, umax = F(1, 225), F(1, 196)
    vmin, vmax = F(1, 484), F(1, 441)
    schur = umin*vmin*(umin-vmax)**2 / (umax+vmax)
    tail = F(10000, 9999)*8*F(50)**(-7)*(F(4, 7)+F(1, 49))
    return {"prefix_schur_lower": schur, "tail_negative_upper": tail,
            "margin": schur-tail, "status": "conditional_on_unverified_zero_inputs"}
