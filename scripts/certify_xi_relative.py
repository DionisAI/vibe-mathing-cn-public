#!/usr/bin/env python3
"""Certify prefix-relative negative-tail budgets, not RH.

The prefix is the complete height-50 critical-line cover from HHT005. Above
50 only full-strip height counts and the strip |beta-1/2|<=1/2 are used. A
large budget means inconclusive, never a counterexample. Infinite remainder
uses the documented N(t)<=t*log(t), t>=50, analytic input.
"""
from __future__ import annotations
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from certify_xi_prefix import zero_cover, xi_value, BRACKETS, PIN
from hht_relative_math import ldl_polynomials, imag_divided, decision

SCALE=200
HEIGHT=50
END=256
REFINEMENTS=128
CELL_DEPTH=6
MAX_COUNT_QUERIES=5000
MAX_REPORT_BYTES=500000


def exact_ball(arb, fmpq, x: F):
    """Embed a rational without passing through a machine float."""
    x=F(x)
    return arb(fmpq(x.numerator,x.denominator))


def closed_ball(arb, fmpq, lo: F, hi: F):
    """Outward enclosure of a rational closed interval."""
    if lo>hi: raise ValueError('reversed interval')
    return arb(exact_ball(arb,fmpq,(lo+hi)/2),exact_ball(arb,fmpq,(hi-lo)/2))


def upper(value) -> F:
    """Export an outward upper bound as an exact rational."""
    if not value.is_finite(): raise ArithmeticError('non-finite bound')
    return F(str(value.upper().fmpq()))


def magnitude(value) -> F:
    """Bound the absolute value, without losing an interval endpoint."""
    if not value.is_finite(): raise ArithmeticError('non-finite polynomial enclosure')
    return max(abs(F(str(value.lower().fmpq()))),abs(F(str(value.upper().fmpq()))))


def refined_prefix(arb,acb,fmpq):
    """Bisection preserves strict brackets for all ten certified prefix roots."""
    roots=[]
    for a,b in BRACKETS:
        lo,hi=F(a),F(b)
        left=xi_value(acb,arb,acb(arb(1)/2,exact_ball(arb,fmpq,lo))).real
        sl=1 if left>0 else -1 if left<0 else 0
        if not sl: raise ArithmeticError('indeterminate initial sign')
        for _ in range(REFINEMENTS):
            mid=(lo+hi)/2
            val=xi_value(acb,arb,acb(arb(1)/2,exact_ball(arb,fmpq,mid)))
            if not val.imag.contains(0): raise ArithmeticError('reality consistency failure')
            sm=1 if val.real>0 else -1 if val.real<0 else 0
            if not sm: raise ArithmeticError('indeterminate refined sign')
            if sm==sl: lo=mid
            else: hi=mid
        roots.append((lo,hi))
    return roots


def counted_cells(arb,fmpq):
    """Count every upper-half-plane zero in (50,256], retaining uncertain splits."""
    cache={}
    def count(t):
        t=F(t)
        if t not in cache:
            if len(cache)>=MAX_COUNT_QUERIES: raise RuntimeError('height count budget exhausted')
            v=exact_ball(arb,fmpq,t).zeta_nzeros().unique_fmpz()
            cache[t]=None if v is None else int(v)
        return cache[t]
    cells=[]
    def split(a,b,na,nb,depth):
        if na is None or nb is None or nb<na: raise ArithmeticError('invalid endpoint count')
        if na==nb: return
        if depth==0:
            cells.append((a,b,nb-na));return
        mid=(a+b)/2;nm=count(mid)
        if nm is None:
            cells.append((a,b,nb-na));return
        if not na<=nm<=nb: raise ArithmeticError('non-monotone zero count')
        split(a,mid,na,nm,depth-1);split(mid,b,nm,nb,depth-1)
    for a in range(HEIGHT,END):
        split(F(a),F(a+1),count(a),count(a+1),CELL_DEPTH)
    if count(HEIGHT)!=10 or sum(n for a,b,n in cells)!=count(END)-10:
        raise ArithmeticError('tail cells do not exhaust the full-strip height count')
    return cells, len(cache), count(END)


def coarse_row(poly, norm, T, arb, fmpq):
    """Coefficient-absolute majorant for the truly infinite remainder."""
    C=exact_ball(arb,fmpq,F(1)/(1-F(1,4*T*T)))
    logT=exact_ball(arb,fmpq,upper(arb(T).log()))
    out=arb(0)
    for i in range(1,len(poly)):
        for j in range(1,len(poly)):
            q=2*i+2*j+4
            Z=q*(logT/(q-1)+arb(1)/(q-1)**2)/arb(T)**(q-1)
            cc=exact_ball(arb,fmpq,magnitude(poly[i])*magnitude(poly[j]))
            out+=i*j*SCALE**(i+j)*cc*Z
    return upper(C*out/norm)


def run_at_precision(bits: int) -> dict:
    """Compute a complete ten-node prefix and two competing all-tail upper bounds."""
    from flint import arb,acb,ctx,fmpq
    if bits not in (384,512): raise ValueError('unexpected precision')
    with ctx.workprec(bits):
        cover=zero_cover(256)
        roots=refined_prefix(arb,acb,fmpq)
        u=[1/closed_ball(arb,fmpq,a,b)**2 for a,b in roots]
        moments=[sum((v*(SCALE*v)**k for v in u),arb(0)) for k in range(19)]
        A=[[moments[i+j] for j in range(10)] for i in range(10)]
        B,D=ldl_polynomials(A)
        polys=[row[:i+1] for i,row in enumerate(B)]
        cells,queries,total=counted_cells(arb,fmpq)
        finite=[F(0)]*10
        for a,b,count in cells:
            # Re(SCALE/lambda) is monotone in g^2 and delta^2 on this strip.
            xlo=SCALE*(b*b-F(1,4))/(b*b+F(1,4))**2
            xhi=F(SCALE)/(a*a)
            X=closed_ball(arb,fmpq,xlo,xhi)
            Y2=closed_ball(arb,fmpq,F(0),F(SCALE*SCALE)/a**6)
            # lossWeight(original u)*Im(SCALE*u)^2 <= multiplier.
            multiplier=F(count*SCALE*SCALE)/(a**8*(1-F(1,4)/(a*a)))
            for i in range(1,10):
                v=magnitude(imag_divided(polys[i],X,Y2))
                finite[i]+=upper(exact_ball(arb,fmpq,multiplier*v*v)/D[i])
        coarse=[coarse_row(p,norm,HEIGHT,arb,fmpq) for p,norm in zip(polys,D)]
        remainder=[coarse_row(p,norm,END,arb,fmpq) for p,norm in zip(polys,D)]
        records=[]
        for d in range(1,11):
            old=sum(coarse[:d],F(0)); part=sum(finite[:d],F(0)); rest=sum(remainder[:d],F(0))
            bound=part+rest
            records.append({'d':d,'coarse_kappa_upper':str(old),
                'coarse_display':format(float(old),'.10g'),
                'cell_part_upper':str(part),'infinite_remainder_upper':str(rest),
                'structured_kappa_upper':str(bound),'structured_display':format(float(bound),'.10g'),
                'decision':decision(bound)})
        return {'precision_bits':bits,'prefix_total':cover['total_count'],
            'refined_height_brackets':[[str(a),str(b)] for a,b in roots],
            'tail_count_at_end':total,'count_queries':queries,
            'counted_cells':[[str(a),str(b),n] for a,b,n in cells],
            'results':records,'off_line_positions_above_50_not_assumed_absent':True,
            'special_functions_lean_certified':False}


def run() -> dict:
    """Two precision reruns; numerical backend trust remains separate from Lean."""
    if importlib.metadata.version('python-flint')!=PIN: raise RuntimeError('backend version drift')
    reports=[run_at_precision(bits) for bits in (384,512)]
    for a,b in zip(reports[0]['results'],reports[1]['results']):
        if a['decision']!=b['decision']: raise ArithmeticError('precision decisions differ')
    return {'schema':'hht006-relative-tail-v1','runs':reports,
        'python_flint':PIN,'height_prefix':HEIGHT,'height_remainder':END,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'analytic_count_input':'HHT004: N(t)<=t*log(t) for t>=50',
        'rh_proved':False,'all_dimensions_proved':False,'canonical_admission':False}


if __name__=='__main__':
    try:
        report=run()
        encoded=json.dumps(report,sort_keys=True,indent=2)+'\n'
        if len(encoded.encode())>MAX_REPORT_BYTES: raise RuntimeError('report exceeds output limit')
        print(encoded,end='')
        print('HHT006_NUMERICAL_PASS: budgets computed; only dimensions with kappa<1 certified; not RH.')
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
