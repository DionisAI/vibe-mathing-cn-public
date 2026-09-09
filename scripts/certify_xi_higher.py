#!/usr/bin/env python3
"""Directly certify larger zero-shift xi Hankel blocks with ball arithmetic.

This uses Taylor coefficients of the actual completed xi expression, not a
finite zero product. A failed/uncertain LDL pivot is INCONCLUSIVE, never a
counterexample. This is finite-dimensional numerical certification, not RH.
"""
from __future__ import annotations
import importlib.metadata
import json
import sys
from certify_xi_prefix import PIN, interval_record, xi_value

DIMENSIONS=(12,16,20,24)
BITS=(768,1024)
SCALE=200


def positive_ldl(matrix):
    n=len(matrix)
    if not 2 <= n <= 24 or any(len(row)!=n for row in matrix):
        raise ValueError('expected square matrix of dimension 2..24')
    work=[list(row) for row in matrix]
    pivots=[]
    for k in range(n):
        pivot=work[k][k]
        if not pivot>0:
            return pivots, k, interval_record(pivot)
        pivots.append(pivot)
        for i in range(k+1,n):
            for j in range(i,n):
                value=work[i][j]-work[i][k]*work[j][k]/pivot
                work[i][j]=value; work[j][i]=value
    return pivots, None, None


def certify(dimension,bits):
    from flint import acb,acb_series,arb,ctx
    if dimension not in DIMENSIONS or bits not in BITS:
        raise ValueError('unsupported bounded run')
    cap=4*dimension
    oldcap=ctx.cap
    try:
        with ctx.workprec(bits):
            ctx.cap=cap
            s=acb_series([acb(arb(1)/2),1],prec=cap)
            completed=xi_value(acb,arb,s)
            if completed.prec<cap: raise ArithmeticError('Taylor truncation shortfall')
            for j in range(cap):
                if not completed[j].imag.contains(0):
                    raise ArithmeticError('Taylor reality check failed')
                if j%2 and not completed[j].real.contains(0):
                    raise ArithmeticError('Taylor evenness check failed')
            f=acb_series([completed[2*j] for j in range(2*dimension)],prec=2*dimension)
            ratio=f.derivative()/f
            if ratio.prec<2*dimension-1: raise ArithmeticError('log derivative shortfall')
            moments=[]
            for n in range(2*dimension-1):
                z=(-1)**n*ratio[n]
                if not z.imag.contains(0): raise ArithmeticError('moment reality failed')
                moments.append(z.real)
            matrix=[[moments[i+j]*SCALE**(i+j) for j in range(dimension)] for i in range(dimension)]
            pivots,failed,bad=positive_ldl(matrix)
            return {'dimension':dimension,'precision_bits':bits,'series_order':cap,
                    'certified_positive_pivots':len(pivots),'first_uncertified_index':failed,
                    'first_uncertified_pivot':bad,
                    'last_positive_pivot':interval_record(pivots[-1]) if pivots else None,
                    'decision':'positive_definite' if failed is None else 'inconclusive',
                    'actual_xi_coefficients':True,'zero_locations_used':False}
    finally:
        ctx.cap=oldcap


def main():
    if importlib.metadata.version('python-flint')!=PIN:
        raise RuntimeError('python-flint version drift')
    rows=[]
    for d in DIMENSIONS:
        pair=[certify(d,b) for b in BITS]
        if pair[0]['decision']!=pair[1]['decision']:
            raise ArithmeticError('precision decisions disagree')
        rows.extend(pair)
        if pair[0]['decision']!='positive_definite':
            break
    report={'schema':'xi-higher-hankel-v1','python_flint':PIN,'runs':rows,
            'rh_proved':False,'all_dimensions_proved':False,'canonical_admission':False}
    print(json.dumps(report,sort_keys=True,indent=2))
    max_ok=max((r['dimension'] for r in rows if r['decision']=='positive_definite'),default=0)
    print(f'XI_HIGHER_PASS: actual xi H1..H{max_ok} certified when both precisions pass; not RH.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr); raise SystemExit(1)
