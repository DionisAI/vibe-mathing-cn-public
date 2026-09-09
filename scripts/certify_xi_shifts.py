#!/usr/bin/env python3
"""All nonnegative shifts for fixed d<=10, with explicit backend/analytic trust.

A finite set of actual xi coefficient matrices plus a geometric interpolation
bound covers infinitely many shifts. No RH assumption or extrapolated root list.
"""
from __future__ import annotations
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from hht_shift_math import anchor_budget,budget,first_certified_shift,grid_outer,positive_ldl
from certify_xi_prefix import PIN,zero_cover,xi_value
from certify_xi_relative import refined_prefix,counted_cells,HEIGHT,END

RADIUS=F(1,256**2)
MASS=F(7,128)
DIMENSION=10
MAX_REPORT_BYTES=300000


def record(value, bits=384):
    """Exact outward grid endpoints; no float used in any acceptance decision."""
    if not value.is_finite():raise ArithmeticError('non-finite enclosure')
    # Very small moments need a finer grid than the finite input helper allows.
    scale=1<<bits
    a=F((F(str(value.lower().fmpq()))*scale).__floor__(),scale)
    b=F((F(str(value.upper().fmpq()))*scale).__ceil__(),scale)
    return [str(a),str(b)]


def actual_moments(count,arb,acb,acb_series,ctx):
    """Coefficients of full xi, not a truncated zero product."""
    if not 1<=count<=64:raise ValueError('coefficient budget exceeded')
    cap=2*(count+1);oldcap=ctx.cap
    try:
        ctx.cap=cap
        s=acb_series([acb(arb(1)/2),1],prec=cap)
        f=xi_value(acb,arb,s)
        if f.prec<cap:raise ArithmeticError('insufficient Taylor order')
        for j in range(cap):
            if not f[j].imag.contains(0):raise ArithmeticError('real coefficient consistency')
            if j%2 and not f[j].real.contains(0):raise ArithmeticError('evenness consistency')
        g=acb_series([f[2*j] for j in range(count+1)],prec=count+1)
        ratio=g.derivative()/g
        if ratio.prec<count:raise ArithmeticError('insufficient logarithmic derivative')
        out=[]
        for n in range(count):
            z=(-1)**n*ratio[n]
            if not z.imag.contains(0):raise ArithmeticError('real moment consistency')
            out.append(z.real)
        return out
    finally:ctx.cap=oldcap


def run_at_precision(bits):
    """Recompute root completeness, geometric constants and all finite exceptions."""
    from flint import arb,acb,acb_series,ctx,fmpq
    if bits not in (1024,1536) or (HEIGHT,END)!=(50,256):
        raise ValueError('frozen experiment inputs changed')
    with ctx.workprec(bits):
        cover=zero_cover(256)
        roots=refined_prefix(arb,acb,fmpq)
        cells,queries,total=counted_cells(arb,fmpq)
        if cover['total_count']!=10 or any(n!=1 for _,_,n in cells):
            raise ArithmeticError('complete prefix not exhausted by singletons')
        # Every singleton full-strip cell is fixed by rho -> 1-conj(rho).
        # This is a theorem, not the assumption beta=1/2 in the count routine.
        boxes=[grid_outer(1/b**2,1/a**2,64) for a,b in roots]
        rows=[]
        for d in range(1,DIMENSION+1):
            cs,aa,Ms=anchor_budget(boxes[:d],RADIUS,MASS)
            K=first_certified_shift(cs,aa)
            if K is None or K>32:raise ArithmeticError('geometric search is inconclusive')
            rows.append({'d':d,'K':K,'budget_at_K':str(budget(cs,aa,K)),
                         'margin_at_K':str(1-budget(cs,aa,K)),
                         'coefficients':[str(c) for c in cs],
                         'contractions':[str(a) for a in aa]})
        K=rows[-1]['K']
        count=max(1,K+2*DIMENSION-2)
        moments=actual_moments(count,arb,acb,acb_series,ctx)
        checks=[]
        for k in range(K):
            scaled=[v*200**(n+1) for n,v in enumerate(moments)]
            matrix=[[scaled[k+i+j] for j in range(DIMENSION)] for i in range(DIMENSION)]
            pivots=positive_ldl(matrix)
            boxes_p=[record(v) for v in pivots]
            if any(F(x[0])<=0 for x in boxes_p):raise ArithmeticError('exported pivot loses strict sign')
            checks.append({'k':k,'dimension':DIMENSION,'scaled_pivot_intervals':boxes_p})
        return {'bits':bits,'verified_height':256,'full_strip_count':total,
            'new_singleton_cells':len(cells),'count_queries':queries,
            'cells':[[str(a),str(b),n] for a,b,n in cells],
            'anchor_height_intervals':[[str(a),str(b)] for a,b in roots],
            'anchor_inverse_intervals':[[str(a),str(b)] for a,b in boxes],
            'tail_radius':str(RADIUS),'tail_mass_bound':str(MASS),
            'shift_budgets':rows,'finite_checks':checks,
            'moments':[record(v) for v in moments],
            'conclusion':'H_(d,k) positive definite for 1<=d<=10 and EVERY integer k>=0',
            'trust':'FLINT special functions/counts + xi symmetry/Hadamard + HHT004 count theorem',
            'all_dimensions_proved':False,'actual_xi_end_to_end_lean':False}


def run():
    """Two full precision runs and interval overlap checks, not independent backends."""
    if importlib.metadata.version('python-flint')!=PIN:raise RuntimeError('backend drift')
    reports=[run_at_precision(b) for b in (1024,1536)]
    for x,y in zip(reports[0]['moments'],reports[1]['moments']):
        if F(x[0])>F(y[1]) or F(y[0])>F(x[1]):raise ArithmeticError('moment enclosures disagree')
    if [r['K'] for r in reports[0]['shift_budgets']] != [r['K'] for r in reports[1]['shift_budgets']]:
        raise ArithmeticError('threshold decisions disagree')
    sources={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
             for name in ('certify_xi_shifts.py','hht_shift_math.py','certify_xi_relative.py','certify_xi_prefix.py')}
    return {'schema':'hht-all-shifts-v1','runs':reports,'sources':sources,'rh_proved':False,
            'canonical_admission':False,'analytic_mass_input':'N(t)<=t log(t), t>=50; log(256)<6'}

if __name__=='__main__':
    try:
        text=json.dumps(run(),sort_keys=True,indent=2)+'\n'
        if len(text.encode())>MAX_REPORT_BYTES:raise RuntimeError('report budget exceeded')
        print(text,end='')
        print('XI_ALL_SHIFTS_PASS: d=1..10, all integer k>=0; not all dimensions or full Lean xi.')
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
