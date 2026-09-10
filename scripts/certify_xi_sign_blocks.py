#!/usr/bin/env python3
"""Rigorous finite dense-direction checks for the actual-xi sign-block corollary.

The general unbounded-term statement is proved by ordered compression in the
mathematical note, not by these examples. No finite zero product is substituted.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from certify_xi_sparse import actual_moments
from certify_xi_prefix import PIN, interval_record
from hht_total_math import leading_positive_pivots

BLOCKS = tuple(tuple(range(5*j, 5*j+5)) for j in range(10))
SHIFTS = (0, 7)
MAX_OUTPUT = 4_000_000


def ball_compression(moments, blocks, shift):
    """Use each symmetric entry once; do not infer symmetry from overlapping balls."""
    from flint import arb
    d = len(blocks)
    if d != 10 or blocks != BLOCKS or shift not in SHIFTS:
        raise ValueError('outside the frozen finite experiment')
    a = [[arb(0) for _ in range(d)] for _ in range(d)]
    for i in range(d):
        for j in range(i, d):
            entry = sum((moments[shift+u+v] for u in blocks[i] for v in blocks[j]), arb(0))
            if not entry.is_finite():
                raise ArithmeticError('nonfinite compressed entry')
            a[i][j] = entry
            a[j][i] = entry
    return a


def run_precision(bits):
    """Certify two dense 50-term examples, each with nine coefficient sign changes."""
    from flint import arb, ctx
    with ctx.workprec(bits):
        n = max(SHIFTS) + 2*BLOCKS[-1][-1]
        mu = actual_moments(n, bits)
        scaled = [m*200**(j+1) for j, m in enumerate(mu)]
        reports = []
        for k in SHIFTS:
            a = ball_compression(scaled, BLOCKS, k)
            pivots = leading_positive_pivots(a)
            signs = [(-1)**j for j in range(len(BLOCKS))]
            grouped = sum((signs[i]*signs[j]*a[i][j]
                           for i in range(10) for j in range(10)), arb(0))
            coeff_sign = [(-1)**(i//5) for i in range(50)]
            direct = sum((coeff_sign[i]*coeff_sign[j]*scaled[k+i+j]
                          for i in range(50) for j in range(50)), arb(0))
            if not (grouped > 0 and direct > 0 and (grouped-direct).contains(0)):
                raise ArithmeticError('direction sign or independent regrouping uncertain')
            reports.append({'shift': k, 'nonzero_terms': 50, 'sign_changes': 9,
                'blocks': BLOCKS, 'coefficient_formula': 'c_i=(-1)^(floor(i/5))*200^i, i=0..49',
                'matrix_normalization': 'C_ij=200^(k+1)*L_k(b_i*b_j), b_j=sum_(e in block_j)200^e X^e',
                'compressed_matrix': [[interval_record(x) for x in row] for row in a],
                'positive_pivot_enclosures': [interval_record(x) for x in pivots],
                'scaled_direction_enclosure': interval_record(grouped),
                'direct_scaled_direction_enclosure': interval_record(direct)})
        return {'bits': bits, 'moment_count': n+1, 'moments': [interval_record(x) for x in mu],
            'cases': reports, 'no_zero_locations_used': True,
            'general_sign_block_theorem_proved_by_examples': False}


def run():
    """Pin the strict backend and require consistent moment enclosures on rerun."""
    if importlib.metadata.version('python-flint') != PIN:
        raise RuntimeError('ball arithmetic version drift')
    reports = [run_precision(bits) for bits in (2048, 3072)]
    for a, b in zip(reports[0]['moments'], reports[1]['moments']):
        if F(a['lower']) > F(b['upper']) or F(b['lower']) > F(a['upper']):
            raise ArithmeticError('disjoint precision reruns')
    directory = Path(__file__).resolve().parent
    return {'schema': 'hht-sign-blocks-v1', 'runs': reports,
        'kernel_input': 'PR12 strict TP10; classical Fekete and frozen PR11 actual-xi inputs',
        'source_sha256': {p: hashlib.sha256((directory/p).read_bytes()).hexdigest()
            for p in ('certify_xi_sign_blocks.py', 'hht_sign_blocks.py', 'certify_xi_sparse.py', 'certify_xi_prefix.py')},
        'actual_xi_end_to_end_lean': False, 'rh_proved': False, 'canonical_admission': False}


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--summary', action='store_true')
        args = parser.parse_args()
        report = run()
        if args.summary:
            digest = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            report['runs'] = [{'bits': r['bits'], 'moment_count': r['moment_count'],
                'cases': [{'shift': c['shift'], 'nonzero_terms': c['nonzero_terms'],
                    'sign_changes': c['sign_changes'],
                    'certified_positive_pivots': len(c['positive_pivot_enclosures']),
                    'last_pivot': c['positive_pivot_enclosures'][-1],
                    'scaled_direction': c['scaled_direction_enclosure']} for c in r['cases']],
                'no_zero_locations_used': True,
                'general_sign_block_theorem_proved_by_examples': False} for r in report['runs']]
            report['full_report_sha256'] = digest
        text = json.dumps(report, indent=2, sort_keys=True)+'\n'
        if len(text.encode()) > MAX_OUTPUT:
            raise RuntimeError('bounded report exceeded')
        print(text, end='')
        print('XI_SIGN_BLOCKS_PASS: two dense 50-term examples at two precisions; general proof uses TP10, not finite samples.')
    except Exception as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
