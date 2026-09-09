#!/usr/bin/env python3
"""Pure-rational interval certificate for an infinite synthetic spectrum.

Its first eight Hankel blocks are positive, while localization exposes a
negative direction in dimension 108. All operations use outward dyadic
rounding; no FLINT, floating-point eigenvalues or zero-table inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'fixtures'))
from hankel_localization import integer, square_spectrum, power


@dataclass(frozen=True)
class Interval:
    """Closed rational interval with fixed absolute dyadic rounding precision."""
    lo: F
    hi: F
    bits: int = 512

    def __post_init__(self):
        """No floats, inverted intervals or unbounded precision are accepted."""
        integer(self.bits,64,1024)
        if any(isinstance(x,bool) or not isinstance(x,(F,int)) for x in (self.lo,self.hi)):
            raise ValueError('exact endpoints required')
        lo,hi=F(self.lo),F(self.hi)
        if lo>hi:
            raise ValueError('inverted interval')
        scale=1<<self.bits
        object.__setattr__(self,'lo',F((lo*scale).__floor__(),scale))
        object.__setattr__(self,'hi',F((hi*scale).__ceil__(),scale))

    def _coerce(self,other):
        """Coerce exact scalars without changing the shared precision."""
        if isinstance(other,Interval):
            if other.bits!=self.bits: raise ValueError('precision mismatch')
            return other
        return Interval(other,other,self.bits)

    def __add__(self,other):
        """Outward-rounded interval addition."""
        other=self._coerce(other)
        return Interval(self.lo+other.lo,self.hi+other.hi,self.bits)

    __radd__=__add__

    def __neg__(self):
        """Exact sign reversal followed by safe outward rounding."""
        return Interval(-self.hi,-self.lo,self.bits)

    def __sub__(self,other):
        """Subtraction retains interval uncertainty."""
        return self+-self._coerce(other)

    def __mul__(self,other):
        """Take extrema over four products, including negative endpoints."""
        other=self._coerce(other)
        values=[x*y for x in (self.lo,self.hi) for y in (other.lo,other.hi)]
        return Interval(min(values),max(values),self.bits)

    __rmul__=__mul__

    def __truediv__(self,other):
        """Division is forbidden when the divisor might be zero."""
        other=self._coerce(other)
        if other.lo<=0<=other.hi: raise ArithmeticError('INCONCLUSIVE: divisor contains zero')
        return self*Interval(1/other.hi,1/other.lo,self.bits)

    def pow(self,n):
        """Bounded integer powers by repeated interval multiplication."""
        n=integer(n,0,64)
        out=Interval(1,1,self.bits); base=self
        while n:
            if n&1: out=out*base
            base=base*base; n>>=1
        return out


def atan_reciprocal(q:int,terms:int)->tuple[F,F]:
    """Alternating arctangent series with an explicit next-term remainder."""
    integer(q,2,1024); integer(terms,1,512)
    s=sum((F((-1)**j,(2*j+1)*q**(2*j+1)) for j in range(terms)),F(0))
    next_term=F((-1)**terms,(2*terms+1)*q**(2*terms+1))
    return min(s,s+next_term),max(s,s+next_term)


def pi_interval(bits:int=512)->Interval:
    """Machin identity pi=16 atan(1/5)-4 atan(1/239), with rational remainders."""
    integer(bits,64,1024)
    terms=bits//4+12
    a,b=atan_reciprocal(5,terms),atan_reciprocal(239,terms)
    return Interval(16*a[0]-4*b[1],16*a[1]-4*b[0],bits)


def bernoulli(n:int)->list[F]:
    """Exact recurrence sum_{k=0}^m binom(m+1,k) B_k=0 for m>=1."""
    integer(n,0,32)
    out=[F(1)]
    for m in range(1,n+1):
        out.append(-sum((comb(m+1,k)*out[k] for k in range(m)),F(0))/(m+1))
    return out


def positive_ldl(matrix:list[list[Interval]])->list[Interval]:
    """Certify a symmetric interval matrix by strictly positive Schur pivots.

Entrywise intervals contain one underlying symmetric matrix. This routine
requires symmetric interval data and never interprets a failed pivot as a
negative certificate. All arithmetic errors propagate out.
"""
    n=integer(len(matrix),1,8)
    if any(len(row)!=n for row in matrix): raise ValueError('nonsquare matrix')
    if any(not isinstance(x,Interval) for row in matrix for x in row):
        raise ValueError('expected Interval entries')
    if any(matrix[i][j]!=matrix[j][i] for i in range(n) for j in range(n)):
        raise ValueError('not symmetric')
    a=[row[:] for row in matrix]; pivots=[]
    for k in range(n):
        pivot=a[k][k]
        if pivot.lo<=0: raise ArithmeticError(f'INCONCLUSIVE: pivot {k+1} not strictly positive')
        pivots.append(pivot)
        for i in range(k+1,n):
            for j in range(i,n):
                value=a[i][j]-(a[i][k]*a[k][j])/pivot
                a[i][j]=value; a[j][i]=value
    return pivots


def certify(bits:int=512)->dict:
    """Certify the FULL synthetic moments, not a finite root approximation."""
    pival=pi_interval(bits); B=bernoulli(30); spec=square_spectrum(F(17,2),F(1,4))
    moments=[]
    for k in range(15):
        j=k+1
        value=(2*pival).pow(2*j)* (abs(B[2*j])/ (2*factorial(2*j)))
        value=value+2*power(spec.target,k+1)[0]
        moments.append(value)
    matrix=[[moments[i+j] for j in range(8)] for i in range(8)]
    pivots=positive_ldl(matrix)
    witness=spec.find_witness()
    return {'bits':bits,'pivots':pivots,'moments':moments,'witness':witness,
            'scope':'synthetic square spectrum, not xi','lean_kernel_checked':False}


if __name__=='__main__':
    results=[certify(bits) for bits in (256,512)]
    for r in results:
        print(f'bits={r["bits"]}: FULL H1..H8 positive; dimension-{r["witness"]["dimension"]} '
              'negative witness includes the entire tail; synthetic only')
        for i,p in enumerate(r['pivots']):
            print(f'pivot[{i+1}] lower={p.lo}')
    for a,b in zip(results[0]['moments'],results[1]['moments']):
        if max(a.lo,b.lo)>min(a.hi,b.hi): raise ArithmeticError('precision disagreement')
    print('HHT006_INTERVAL_PASS: exact rational enclosures, not Lean and not RH.')
