#!/usr/bin/env python3
"""Recompute a complete low-height zero cover and direct xi coefficient bounds.

Uses pinned FLINT ball arithmetic, not approximate zero tables or floating-point
sign tests. This executable is a numerical certification backend, not a Lean
kernel proof of the zeta/gamma implementations or a canonical Result verifier.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

PIN = "0.8.0"
CUTOFF = 50
BRACKETS = ((14, 15), (21, 22), (25, 26), (30, 31), (32, 33),
            (37, 38), (40, 41), (43, 44), (48, 49), (49, 50))


def check_brackets(brackets, cutoff: int) -> tuple[tuple[int, int], ...]:
    """Validate disjoint open brackets; their nonzero endpoints are tested later."""
    if isinstance(cutoff, bool) or not isinstance(cutoff, int) or not 1 <= cutoff <= 1000:
        raise ValueError("invalid bounded height cutoff")
    if not isinstance(brackets, (list, tuple)) or not 1 <= len(brackets) <= 32:
        raise ValueError("invalid bracket count")
    out = []
    for pair in brackets:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("expected two integer endpoints")
        a, b = pair
        if any(isinstance(t, bool) or not isinstance(t, int) for t in pair):
            raise ValueError("integer endpoints are required")
        if not 0 < a < b <= cutoff or (out and a < out[-1][1]):
            raise ValueError("unordered, overlapping, or out-of-height bracket")
        out.append((a, b))
    return tuple(out)


def check_cover_logic(brackets, cutoff: int, endpoint_signs: dict[int, int],
                      total_count: int) -> None:
    """Check the finite counting implication, not the truth of backend evaluations."""
    brackets = check_brackets(brackets, cutoff)
    if isinstance(total_count, bool) or not isinstance(total_count, int):
        raise ValueError("count must be a certified integer")
    if total_count != len(brackets):
        raise ValueError("number of disjoint sign brackets does not exhaust total count")
    for a, b in brackets:
        sa, sb = endpoint_signs.get(a), endpoint_signs.get(b)
        if (type(sa) is not int or type(sb) is not int or
                sa not in (-1, 1) or sb not in (-1, 1) or sa == sb):
            raise ValueError("strict opposite endpoint signs are required")


def interval_record(value) -> dict[str, str]:
    """Serialize outward-rounded exact dyadic endpoints, never midpoint-only text."""
    if not value.is_finite():
        raise ArithmeticError("non-finite ball")
    return {"lower": str(value.lower().fmpq()), "upper": str(value.upper().fmpq()),
            "display": str(value)}


def xi_value(acb, arb, s):
    """Evaluate the classical completed xi expression away from its removable poles."""
    return s * (s - 1) * (-s * arb.pi().log() / 2).exp() * (s / 2).gamma() * s.zeta() / 2


def zero_cover(bits: int = 128) -> dict:
    """Count all strip zeros and exhaust the count with disjoint critical-line roots."""
    from flint import acb, arb, ctx
    brackets = check_brackets(BRACKETS, CUTOFF)
    with ctx.workprec(bits):
        count_ball = arb(CUTOFF).zeta_nzeros()
        count = count_ball.unique_fmpz()
        if count is None:
            raise ArithmeticError("total zero count was not isolated as one integer")
        signs, evidence = {}, {}
        for t in sorted({t for pair in brackets for t in pair}):
            value = xi_value(acb, arb, acb(arb(1) / 2, t))
            # Reality follows from xi(1-s)=xi(s) and conjugation, not this test.
            if not value.imag.contains(0):
                raise ArithmeticError("xi critical-line reality consistency check failed")
            if value.real > 0:
                signs[t] = 1
            elif value.real < 0:
                signs[t] = -1
            else:
                raise ArithmeticError(f"endpoint {t} has indeterminate sign")
            evidence[str(t)] = {**interval_record(value.real), "sign": signs[t]}
        check_cover_logic(brackets, CUTOFF, signs, int(count))
        return {"precision_bits": bits, "cutoff": CUTOFF,
                "count_includes_multiplicity_and_off_line_zeros": True,
                "total_count": int(count), "count_ball": interval_record(count_ball),
                "brackets": brackets, "xi_endpoint_enclosures": evidence,
                "conclusion": "all 10 zeros at 0<Im(rho)<=50 are simple and on the critical line",
                "trust": "FLINT ball algorithms plus classical xi symmetry and intermediate value theorem",
                "lean_certified_special_functions": False}


def positive_ldl(matrix) -> list:
    """Enclose exact Schur pivots; uncertainty never counts as positivity."""
    n = len(matrix)
    if not 1 <= n <= 16 or any(len(row) != n for row in matrix):
        raise ValueError("expected a bounded nonempty square matrix")
    work = [list(row) for row in matrix]
    pivots = []
    for k in range(n):
        pivot = work[k][k]
        if not pivot > 0:
            raise ArithmeticError(f"pivot {k + 1} is not certified strictly positive: {pivot}")
        pivots.append(pivot)
        for i in range(k + 1, n):
            for j in range(i, n):
                value = work[i][j] - work[i][k] * work[j][k] / pivot
                work[i][j] = value
                work[j][i] = value
    return pivots


def direct_xi_coefficients(dimension: int = 8, bits: int = 512) -> dict:
    """Certify fixed Hankel blocks from xi's Taylor series, without any zero input."""
    from flint import acb, acb_series, arb, ctx
    if type(dimension) is not int or not 2 <= dimension <= 12:
        raise ValueError("dimension must be an integer between 2 and 12")
    cap = 4 * dimension
    oldcap = ctx.cap
    try:
        with ctx.workprec(bits):
            ctx.cap = cap
            s = acb_series([acb(arb(1) / 2), 1], prec=cap)
            completed = xi_value(acb, arb, s)
            if completed.prec < cap:
                raise ArithmeticError("unexpected Taylor truncation order")
            for j in range(cap):
                if not completed[j].imag.contains(0):
                    raise ArithmeticError("real Taylor coefficient consistency check failed")
                if j % 2 and not completed[j].real.contains(0):
                    raise ArithmeticError("evenness consistency check failed")
            # F(z)=xi(1/2+sqrt(z))/xi(1/2); normalization cancels in F'/F.
            f = acb_series([completed[2 * j] for j in range(2 * dimension)],
                           prec=2 * dimension)
            derivative_ratio = f.derivative() / f
            if derivative_ratio.prec < 2 * dimension - 1:
                raise ArithmeticError("insufficient logarithmic-derivative precision")
            moments = []
            for n in range(2 * dimension - 1):
                value = (-1) ** n * derivative_ratio[n]
                if not value.imag.contains(0):
                    raise ArithmeticError("moment reality consistency check failed")
                moments.append(value.real)
            # Congruence by diag(1,200,200^2,...) improves scaling, not the sign.
            matrix = [[moments[i + j] * 200 ** (i + j) for j in range(dimension)]
                      for i in range(dimension)]
            pivots = positive_ldl(matrix)
            determinant2 = moments[0] * moments[2] - moments[1] ** 2
            if not determinant2 > 0:
                raise ArithmeticError("direct unscaled H2 determinant check failed")
            return {"precision_bits": bits, "dimension": dimension,
                    "series_order": cap, "moment_count": len(moments),
                    "moment_enclosures": [interval_record(v) for v in moments],
                    "scaled_ldl_pivots": [interval_record(v) for v in pivots],
                    "h2_determinant": interval_record(determinant2),
                    "conclusion": f"H_(d,0) positive definite for each integer 1<=d<={dimension}",
                    "no_zero_locations_used": True,
                    "no_assertion_for_larger_dimensions_or_shifts": True,
                    "lean_certified_special_functions": False}
    finally:
        ctx.cap = oldcap


def run() -> dict:
    """Run two precision levels and retain the full bounded backend evidence."""
    version = importlib.metadata.version("python-flint")
    if version != PIN:
        raise RuntimeError(f"expected python-flint {PIN}, got {version}")
    roots = [zero_cover(bits) for bits in (128, 256)]
    direct = [direct_xi_coefficients(8, bits) for bits in (512, 768)]
    for low, high in zip(direct[0]["moment_enclosures"], direct[1]["moment_enclosures"]):
        if not (Fraction(low["lower"]) <= Fraction(high["upper"]) and
                Fraction(high["lower"]) <= Fraction(low["upper"])):
            raise ArithmeticError("two precision runs produced disjoint moment intervals")
    return {"schema": "hht005-numerical-evidence-v1", "python_flint": version,
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "root_cover": roots, "direct_coefficients": direct,
            "rh_proved": False, "canonical_admission": False}


def main() -> int:
    """Print bounded evidence; optionally save the same JSON to a local artifact."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if len(encoded.encode()) > 500_000:
        raise RuntimeError("report exceeds output budget")
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    print("HHT005_NUMERICAL_PASS: complete height-50 cover and direct H1..H8; not RH or full Lean.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
