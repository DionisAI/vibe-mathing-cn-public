#!/usr/bin/env python3
"""Actual-xi ball checks for rescued directions; no zero locations are inputs."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from certify_xi_sparse import actual_moments
from certify_xi_prefix import interval_record, PIN
from hht_balance import classify_balance, rescued_family, XI_LOWER_RATIO, XI_RADIUS


def run_precision(bits: int) -> dict:
    """Recompute full moments and evaluate both quadratic organizations strictly."""
    from flint import arb, ctx
    with ctx.workprec(bits):
        mu=actual_moments(107,bits)
        ratio=mu[1]/mu[0]
        if not (mu[0]>0 and ratio>arb(1)/625 and ratio<arb(1)/196):
            raise ArithmeticError('new initial-ratio enclosure failed')
        scaled=[v*196**(i+1) for i,v in enumerate(mu)]
        records=[]
        for N in (5,25):
            terms=rescued_family(N)
            cert=classify_balance(terms)
            if cert['old_amplitude_condition_holds'] or cert['status']!='conditional_strict_positive':
                raise ArithmeticError('the test must be outside the old cone')
            coefficients=[(i,v/F(196**i)) for i,v in terms]
            def ball(q): return arb(q.numerator)/q.denominator
            square={}
            for i,a in coefficients:
                for j,b in coefficients:
                    square[i+j]=square.get(i+j,F(0))+a*b
            L=F(cert['lower_multiplier'])
            for k in (0,7):
                q=sum((ball(a)*ball(b)*scaled[k+i+j]
                       for i,a in coefficients for j,b in coefficients),arb(0))
                q2=sum((ball(a)*scaled[k+i] for i,a in square.items()),arb(0))
                gap=q-ball(L)*scaled[k]
                gap2=q2-ball(L)*scaled[k]
                if not(q>0 and q2>0 and gap>0 and gap2>0 and (q-q2).contains(0)):
                    raise ArithmeticError('direction or certified lower bound failed')
                records.append({'N':N,'shift':k,'terms':len(terms),'sign_changes':2*N-1,
                                'constant':1,'opposite_mass':2,'lower_multiplier':str(L),
                                'scaled_Q':interval_record(q),
                                'convolution_Q':interval_record(q2),
                                'normalized_Q_over_mu':interval_record(q/scaled[k]),
                                'strict_gap_above_bound':interval_record(gap)})
        return {'bits':bits,'moment_count':len(mu),'no_zero_locations_used':True,
                'initial_ratio':interval_record(ratio),
                'moments':[interval_record(x) for x in mu], 'cases':records}


def run() -> dict:
    """Execute two precisions of the same pinned backend; keep its trust boundary explicit."""
    if importlib.metadata.version('python-flint')!=PIN:
        raise RuntimeError('backend version drift')
    reports=[run_precision(b) for b in (2048,3072)]
    for a,b in zip(reports[0]['moments'],reports[1]['moments']):
        if F(a['lower'])>F(b['upper']) or F(b['lower'])>F(a['upper']):
            raise ArithmeticError('disjoint moment enclosures')
    paths=('certify_xi_balance.py','hht_balance.py','hht_coefficient_cone.py',
           'certify_xi_sparse.py','certify_xi_prefix.py')
    root=Path(__file__).resolve().parent
    return {'schema':'hht-xi-balance-v1','runs':reports,'python_flint':PIN,
            'ratio_lower':str(XI_LOWER_RATIO),'ratio_upper':str(XI_RADIUS),
            'universal_family_margin':'498624/390625',
            'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
            'infinite_ratio_propagation_uses_frozen_PR11':True,
            'analytic_xi_end_to_end_Lean':False,'rh_proved':False,'canonical_admission':False}


if __name__=='__main__':
    try:
        parser=argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--summary',action='store_true')
        args=parser.parse_args();report=run()
        if args.summary:
            report['full_report_sha256']=hashlib.sha256(json.dumps(report,sort_keys=True).encode()).hexdigest()
            for run_report in report['runs']:
                run_report.pop('moments')
                for case in run_report['cases']:
                    case['normalized_Q_display']=case.pop('normalized_Q_over_mu')['display']
                    case['strict_gap_display']=case.pop('strict_gap_above_bound')['display']
                    case.pop('scaled_Q');case.pop('convolution_Q')
        text=json.dumps(report,sort_keys=True,indent=2)+'\n'
        if len(text.encode())>2_000_000:raise RuntimeError('output budget exceeded')
        print(text,end='')
        print('XI_BALANCE_PASS: initial ratio and four formerly uncovered dense directions at two precisions; NOT all polynomials or RH.')
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr);raise SystemExit(1) from exc
