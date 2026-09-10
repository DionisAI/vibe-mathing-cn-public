#!/usr/bin/env python3
"""Certify eventual positive blocks up to order 111, not a cofinal family or RH.

Uses full-strip root counting and a bound on ALL unknown zeros above height256.
No finite-root product is substituted for the complete Hankel quadratic form.
"""
from __future__ import annotations
from fractions import Fraction as F
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from certify_xi_prefix import zero_cover,PIN
from certify_xi_relative import refined_prefix,counted_cells,HEIGHT,END
from hht_shift_math import grid_outer
from hht_cofinal import positive_prefix_envelope,threshold,synthetic_certificate

ORDERS=(10,20,40,80,111)
RADIUS=F(1,65536)
MASS=F(7,128)
MAX_OUTPUT=500000


def run_at_precision(bits):
    """Complete counted root intervals, then exact contracting-budget certificates."""
    from flint import arb,acb,ctx,fmpq
    if bits not in (1024,1536) or (HEIGHT,END)!=(50,256):
        raise ValueError('frozen experiment drift')
    with ctx.workprec(bits):
        cover=zero_cover(256)
        first=refined_prefix(arb,acb,fmpq)
        cells,queries,total=counted_cells(arb,fmpq)
        if cover['total_count']!=10 or total!=111 or len(cells)!=101 or any(n!=1 for a,b,n in cells):
            raise ArithmeticError('complete full-strip singleton coverage not established')
        roots=first+[(a,b) for a,b,n in cells]
        if len(roots)!=111 or any(b>=c for (a,b),(c,d) in zip(roots,roots[1:])):
            raise ArithmeticError('height intervals not strictly separated')
        boxes=[grid_outer(1/b**2,1/a**2,64) for a,b in roots]
        rows=[]
        for d in ORDERS:
            C,alpha=positive_prefix_envelope(boxes[:d],RADIUS,MASS)
            cert=threshold(C,alpha)
            if cert is None:
                raise ArithmeticError('threshold search exhausted; not a counterexample')
            rows.append({'order':d,'K':cert['K'],'aggregate_C':str(C),
                         'max_contraction':str(alpha),'power_precision_bits':cert['bits'],
                         'budget_at_K_upper':str(cert['upper']),
                         'budget_display':float(cert['upper']),
                         'all_shifts_k_at_least_K_certified':True})
        return {'bits':bits,'full_strip_count':total,'new_singleton_cells':len(cells),
                'count_queries':queries,'height_intervals':[[str(a),str(b)] for a,b in roots],
                'inverse_intervals':[[str(a),str(b)] for a,b in boxes],
                'tail_radius':str(RADIUS),'complete_tail_mass_upper':str(MASS),
                'thresholds':rows,'all_small_shifts_checked_here':False}


def run():
    sys.set_int_max_str_digits(50000)
    if importlib.metadata.version('python-flint')!=PIN:
        raise RuntimeError('pinned numerical backend drift')
    reports=[run_at_precision(b) for b in (1024,1536)]
    if reports[0]['thresholds']!=reports[1]['thresholds']:
        raise ArithmeticError('exact certificates disagree across precision reruns')
    root=Path(__file__).resolve().parent
    files=('hht_cofinal.py','certify_xi_cofinal.py','certify_xi_relative.py','certify_xi_prefix.py')
    return {'schema':'hht-cofinal-v1','actual_xi_runs':reports,
            'synthetic_infinite_obstruction':synthetic_certificate(),
            'sources':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},
            'analytic_input':'N(t)<=t log(t), t>=50; xi symmetry and Hadamard correspondence',
            'cofinal_actual_xi_family_proved':False,'rh_proved':False,
            'actual_xi_end_to_end_lean':False,'canonical_admission':False}

if __name__=='__main__':
    try:
        parser=argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--summary',action='store_true')
        args=parser.parse_args();report=run()
        if args.summary:
            digest=hashlib.sha256(json.dumps(report,sort_keys=True).encode()).hexdigest()
            for r in report['actual_xi_runs']:
                r.pop('height_intervals');r.pop('inverse_intervals')
                for row in r['thresholds']:
                    row.pop('aggregate_C');row.pop('budget_at_K_upper')
            synth=report['synthetic_infinite_obstruction']
            report['synthetic_infinite_obstruction']={k:synth[k] for k in
                ('dimension','K','alpha','budget_display','statement','actual_xi_counterexample')}
            report['full_report_sha256']=digest
        text=json.dumps(report,sort_keys=True,indent=2)
        if len(text.encode())>MAX_OUTPUT:
            raise RuntimeError('output budget exceeded')
        print(text)
        print('XI_COFINAL_PASS: eventual d<=111 certificates and synthetic all-late-shift obstruction; NOT a cofinal xi family or RH.')
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
