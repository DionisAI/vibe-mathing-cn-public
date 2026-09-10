#!/usr/bin/env python3
"""Strict ball checks of actual xi sparse minors and the next-order frontier.

The infinite-index TP10 theorem uses PR11 plus classical Fekete; the examples
here only cross-check that theorem. They do not prove its infinite quantifiers.
No zero locations or truncated zero products are used in this calculation.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from certify_xi_prefix import xi_value, PIN, interval_record
from hht_total_math import selected, leading_positive_pivots

SUPPORT = (0, 1, 3, 6, 10, 15, 21, 28, 36, 45)
CASES = ((SUPPORT, SUPPORT, 0), (SUPPORT, SUPPORT, 7),
         (SUPPORT, (0, 2, 4, 7, 11, 16, 22, 29, 37, 46), 3),
         ((0, 5, 20, 40), (0, 5, 20, 40), 11))
MAX_OUTPUT = 2_000_000


def actual_moments(n: int, bits: int):
    """Enclose mu_0 through mu_n using the completed zeta expression."""
    from flint import arb, acb, acb_series, ctx
    if type(n) is not int or not 2 <= n <= 128 or bits not in (2048, 3072):
        raise ValueError('unexpected arithmetic budget')
    if ctx.prec != bits:
        raise ValueError('precision label does not match active ball context')
    cap = 2*(n+2)
    oldcap = ctx.cap
    try:
        ctx.cap = cap
        s = acb_series([acb(arb(1)/2), 1], prec=cap)
        value = xi_value(acb, arb, s)
        if value.prec < cap:
            raise ArithmeticError('insufficient Taylor order')
        for j in range(cap):
            if not value[j].imag.contains(0) or (j % 2 and not value[j].real.contains(0)):
                raise ArithmeticError('xi symmetry consistency check failed')
        f = acb_series([value[2*j] for j in range(n+2)], prec=n+2)
        ratio = f.derivative()/f
        if ratio.prec < n+1:
            raise ArithmeticError('insufficient moment order')
        mu = []
        for j in range(n+1):
            v = (-1)**j * ratio[j]
            if not v.imag.contains(0):
                raise ArithmeticError('nonreal moment enclosure')
            mu.append(v.real)
        return mu
    finally:
        ctx.cap = oldcap


def run_precision(bits: int) -> dict:
    """Check selected gapped matrices and five finite next-order curvatures."""
    from flint import arb, ctx
    with ctx.workprec(bits):
        n = max(k+rows[-1]+cols[-1] for rows, cols, k in CASES)
        mu = actual_moments(n, bits)
        # Positive row/column diagonal rescaling changes no minor signs.
        scaled = [m*200**(j+1) for j, m in enumerate(mu)]
        records = []
        for rows, cols, k in CASES:
            ps = leading_positive_pivots(selected(scaled, rows, cols, k))
            records.append({'rows': rows, 'columns': cols, 'shift': k,
                'pivot_enclosures': [interval_record(p) for p in ps],
                'claim': 'positive_definite' if rows == cols else 'positive_minor_only'})
        cache = {}
        def t(d, k):
            if (d, k) not in cache:
                a = selected(scaled, tuple(range(d)), tuple(range(d)), k)
                det = arb(1)
                for pivot in leading_positive_pivots(a):
                    det *= pivot
                cache[d, k] = det
            return cache[d, k]
        frontier = []
        for k in range(5):
            left, middle, right = t(10, k), t(10, k+1), t(10, k+2)
            defect = left*right-middle**2
            independent = t(11, k)*t(9, k+2)
            if not (defect > 0 and independent > 0 and (defect-independent).contains(0)):
                raise ArithmeticError('frontier positivity or identity is indeterminate')
            frontier.append({'shift': k, 'normalized_logconvexity_defect':
                             interval_record(defect/(left*right)),
                             'independent_determinant_product': interval_record(independent)})
        return {'precision_bits': bits, 'moment_count': n+1, 'no_zero_locations_used': True,
                'moments': [interval_record(x) for x in mu], 'sparse_examples': records,
                'order_10_frontier_finite_checks': frontier,
                'finite_extra_conclusion': 'H_(11,k) positive definite for k=0..4 only',
                'all_order_11_shifts_proved': False, 'all_dimensions_proved': False}


def run() -> dict:
    """Repeat at two precisions and require overlapping actual moment enclosures."""
    if importlib.metadata.version('python-flint') != PIN:
        raise RuntimeError('numerical backend version drift')
    reports = [run_precision(b) for b in (2048, 3072)]
    for a, b in zip(reports[0]['moments'], reports[1]['moments']):
        if F(a['lower']) > F(b['upper']) or F(b['lower']) > F(a['upper']):
            raise ArithmeticError('disjoint precision rerun enclosures')
    root = Path(__file__).resolve().parent
    return {'schema': 'hht-total-sparse-v1', 'runs': reports, 'python_flint': PIN,
            'source_sha256': {p: hashlib.sha256((root/p).read_bytes()).hexdigest()
                for p in ('certify_xi_sparse.py', 'hht_total_math.py', 'certify_xi_prefix.py')},
            'full_TP10_input': 'PR11 all shifted contiguous minors + Fekete lemma 2.4',
            'full_TP10_lean_formalized': False, 'rh_proved': False, 'canonical_admission': False}


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--summary', action='store_true', help='Print compact execution summary; omit for full interval evidence')
        args = parser.parse_args()
        report = run()
        if args.summary:
            digest = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            report['runs'] = [{
                'precision_bits': r['precision_bits'], 'moment_count': r['moment_count'],
                'no_zero_locations_used': r['no_zero_locations_used'],
                'sparse_examples': [{
                    'rows': c['rows'], 'columns': c['columns'], 'shift': c['shift'],
                    'claim': c['claim'], 'certified_positive_pivots': len(c['pivot_enclosures']),
                    'last_pivot_display': c['pivot_enclosures'][-1]['display']}
                    for c in r['sparse_examples']],
                'frontier': [{'shift': f['shift'], 'normalized_defect_display':
                    f['normalized_logconvexity_defect']['display']}
                    for f in r['order_10_frontier_finite_checks']],
                'finite_extra_conclusion': r['finite_extra_conclusion'],
                'all_order_11_shifts_proved': False, 'all_dimensions_proved': False}
                for r in report['runs']]
            report['full_report_sha256'] = digest
        text = json.dumps(report, sort_keys=True, indent=2)+'\n' 
        if len(text.encode()) > MAX_OUTPUT:
            raise RuntimeError('report exceeds output limit')
        print(text, end='')
        print('XI_SPARSE_PASS: four sparse examples and five finite H11 blocks; not all H11 shifts or RH.')
    except Exception as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
