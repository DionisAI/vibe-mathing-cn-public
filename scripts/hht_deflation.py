#!/usr/bin/env python3
"""Exact finite-prefix deflation and Schur checks; no assumed global positivity."""
from __future__ import annotations
from fractions import Fraction as F
from hht_balance import classify_balance

MAX_DEGREE = 256
MAX_DIMENSION = 24
MAX_BITS = 32768


def rat(x):
    """Reject inexact arithmetic and excessive exact input/intermediate sizes."""
    if isinstance(x, bool) or not isinstance(x, (int, F)):
        raise ValueError('exact integer or Fraction required')
    x = F(x)
    if max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ValueError('rational budget exceeded')
    return x


def poly(p):
    """Ascending coefficients, with one canonical representation of zero."""
    if not isinstance(p, (list, tuple)) or not 1 <= len(p) <= MAX_DEGREE+1:
        raise ValueError('polynomial shape or degree budget')
    p = [rat(x) for x in p]
    while len(p)>1 and not p[-1]: p.pop()
    return p


def add(p,q):
    """Add bounded rational polynomials."""
    p,q=poly(p),poly(q)
    return poly([rat((p[i] if i<len(p) else 0)+(q[i] if i<len(q) else 0))
                 for i in range(max(len(p),len(q)))])


def mul(p,q):
    """Convolve exactly, checking intermediate bounds."""
    p,q=poly(p),poly(q)
    if len(p)+len(q)-2>MAX_DEGREE: raise ValueError('product degree budget')
    out=[F(0)]*(len(p)+len(q)-1)
    for i,x in enumerate(p):
        for j,y in enumerate(q): out[i+j]=rat(out[i+j]+x*y)
    return poly(out)


def ev(p,x):
    """Exact Horner evaluation."""
    x=rat(x);z=F(0)
    for a in reversed(poly(p)): z=rat(z*x+a)
    return z


def annihilator(nodes):
    """Monic product over distinct positive rational nodes."""
    if not isinstance(nodes,(list,tuple)) or not 1<=len(nodes)<=MAX_DEGREE:
        raise ValueError('anchor count budget')
    nodes=[rat(x) for x in nodes]
    if any(x<=0 for x in nodes) or len(set(nodes))!=len(nodes):
        raise ValueError('distinct positive anchors required')
    out=[F(1)]
    for x in nodes:out=mul(out,[-x,F(1)])
    return out


def split_monic(p,A):
    """Return r,q with p=r+A*q and degree(r)<degree(A)."""
    p,A=poly(p),poly(A)
    if len(A)<2 or A[-1]!=1:raise ValueError('positive-degree monic divisor required')
    r=list(p);q=[F(0)]*max(1,len(p)-len(A)+1)
    while len(r)>=len(A) and r!=[0]:
        j=len(r)-len(A);v=r[-1];q[j]=v
        for i,a in enumerate(A):r[i+j]=rat(r[i+j]-v*a)
        r=poly(r)
    return poly(r),poly(q)


def bilinear(mu,p,q,k=0):
    """Finite coefficient formula using supplied COMPLETE moments."""
    p,q=poly(p),poly(q)
    if type(k) is not int or not 0<=k<=512:raise ValueError('nonnegative bounded integral shift required')
    if not isinstance(mu,(list,tuple)) or not 1<=len(mu)<=1024 or k+len(p)+len(q)-2>=len(mu):
        raise ValueError('insufficient moments; no missing moment defaults')
    m=[rat(x) for x in mu];out=F(0)
    for i,a in enumerate(p):
        for j,b in enumerate(q):out=rat(out+a*b*m[k+i+j])
    return out


def deflated_moments(mu,A,count):
    """nu_n = sum A_i A_j mu_(n+i+j), with no inherited sign assertion."""
    if type(count) is not int or not 1<=count<=2*MAX_DIMENSION+1:
        raise ValueError('deflated moment budget')
    return [bilinear(mu,A,A,k) for k in range(count)]


def matrix(M):
    """Validate a nonempty bounded exact rectangular matrix."""
    if not isinstance(M,(list,tuple)) or not 1<=len(M)<=MAX_DIMENSION:
        raise ValueError('matrix row budget')
    if not isinstance(M[0],(list,tuple)) or not 1<=len(M[0])<=MAX_DIMENSION:
        raise ValueError('matrix column budget')
    n=len(M[0])
    if any(not isinstance(r,(list,tuple)) or len(r)!=n for r in M):
        raise ValueError('ragged matrix')
    return [[rat(x) for x in r] for r in M]


def transpose(A):
    """Validated exact transpose."""
    return [list(r) for r in zip(*matrix(A))]


def matmul(A,B):
    """Matrix multiplication without float conversions."""
    A,B=matrix(A),matrix(B)
    if len(A[0])!=len(B):raise ValueError('matrix product shape')
    out=[]
    for r in A:
        row=[]
        for c in zip(*B):
            x=F(0)
            for a,b in zip(r,c):x=rat(x+a*b)
            row.append(x)
        out.append(row)
    return out


def ldl(A):
    """Exact positive LDL; refusal is not automatically an RH counterexample."""
    A=matrix(A);n=len(A)
    if len(A[0])!=n or A!=transpose(A):raise ValueError('symmetric square matrix required')
    L=[[F(i==j) for j in range(n)] for i in range(n)];d=[]
    for j in range(n):
        pivot=rat(A[j][j]-sum(L[j][s]**2*d[s] for s in range(j)))
        if pivot<=0:raise ArithmeticError('nonpositive exact pivot')
        d.append(pivot)
        for i in range(j+1,n):
            L[i][j]=rat((A[i][j]-sum(L[i][s]*L[j][s]*d[s] for s in range(j)))/pivot)
    return L,d


def determinant(A):
    """Pivoted exact elimination, independent of positive LDL and sign assumptions."""
    A=matrix(A);n=len(A)
    if len(A[0])!=n:raise ValueError('square determinant required')
    result=F(1)
    for j in range(n):
        pivot=next((i for i in range(j,n) if A[i][j]),None)
        if pivot is None:return F(0)
        if pivot!=j:A[j],A[pivot]=A[pivot],A[j];result=-result
        v=A[j][j];result=rat(result*v)
        for i in range(j+1,n):
            t=rat(A[i][j]/v)
            for k in range(j+1,n):A[i][k]=rat(A[i][k]-t*A[j][k])
            A[i][j]=F(0)
    return result


def solve_spd(C,E):
    """Solve C*X=E using checked exact positive LDL."""
    C,E=matrix(C),matrix(E);L,d=ldl(C);n=len(C)
    if len(E)!=n:raise ValueError('right-hand-side shape')
    out=[[F(0)]*len(E[0]) for _ in range(n)]
    for j in range(len(E[0])):
        y=[]
        for i in range(n):y.append(rat(E[i][j]-sum(L[i][s]*y[s] for s in range(i))))
        z=[rat(y[i]/d[i]) for i in range(n)];x=[F(0)]*n
        for i in reversed(range(n)):x[i]=rat(z[i]-sum(L[s][i]*x[s] for s in range(i+1,n)))
        for i in range(n):out[i][j]=x[i]
    return out


def schur(C,E,D):
    """Return D-E^T*C^-1*E, checking shapes, symmetry and positivity of C."""
    C,E,D=matrix(C),matrix(E),matrix(D)
    if len(E)!=len(C) or len(E[0])!=len(D) or len(D[0])!=len(D) or D!=transpose(D):
        raise ValueError('incompatible blocks')
    loss=matmul(transpose(E),solve_spd(C,E))
    return [[rat(D[i][j]-loss[i][j]) for j in range(len(D))] for i in range(len(D))]


def deflation_blocks(mu,A,tail_dimension,k=0):
    """Full Gram matrix in the basis 1,..,X^(N-1),A,..,X^(m-1)A."""
    A=poly(A);N=len(A)-1
    if A[-1]!=1 or N<1 or type(tail_dimension) is not int or tail_dimension<1 or N+tail_dimension>MAX_DIMENSION:
        raise ValueError('monic block basis or dimension budget')
    low=[[F(0)]*j+[F(1)] for j in range(N)]
    high=[[F(0)]*j+A for j in range(tail_dimension)]
    C=[[bilinear(mu,p,q,k) for q in low] for p in low]
    E=[[bilinear(mu,p,q,k) for q in high] for p in low]
    D=[[bilinear(mu,p,q,k) for q in high] for p in high]
    return C,E,D


def root_barrier(p,x,low,high):
    """Check a rational instance of the universal root obstruction."""
    p=poly(p);x,low,high=map(rat,(x,low,high))
    if not 0<low<=x<=high or ev(p,x)!=0 or p==[0]:
        raise ValueError('nonzero polynomial with a root in the ratio interval required')
    result=classify_balance([(i,c) for i,c in enumerate(p) if c],low,high)
    if F(result['lower_multiplier'])>0:raise ArithmeticError('root obstruction violated')
    return result


def signed_moment(n):
    """Explicit indefinite countermodel, NOT actual xi or an unsigned zero spectrum."""
    if type(n) is not int or not 0<=n<=2*MAX_DEGREE:raise ValueError('moment index budget')
    return F(1)+F(1,2)**(n+1)-F(1,2)*F(1,4)**(n+1)


def report():
    """Reproduce exact counterexamples, rather than asserting a new xi result."""
    mu=[signed_moment(n) for n in range(16)]
    A=annihilator([F(1,4)]);C,E,D=deflation_blocks(mu,A,2);S=schur(C,E,D)
    _,cd=ldl(C);_,dd=ldl(D)
    q=[F(1,2),-F(3,2),F(1)];r,s=split_monic(q,A)
    if bilinear(mu,q,q)!=-F(9,2048):raise ArithmeticError('negative countermodel changed')
    nu=deflated_moments(mu,annihilator([F(1)]),3)
    witness111=annihilator([F(1,j*j) for j in range(15,126)])
    barrier=root_barrier(witness111,F(1,225),F(1,625),F(1,196))
    return {'schema':'hht-deflation-v1','example_is_signed_countermodel_not_xi':True,
            'head_pivots':cd,'complement_pivots':dd,'mixed_block':E,
            'schur':S,'schur_determinant':S[0][0]*S[1][1]-S[0][1]**2,
            'negative_polynomial':q,'remainder':r,'quotient':s,
            'full_negative_value':bilinear(mu,q,q),
            'deflation_at_one_moments':nu,'deflated_order2_determinant':nu[0]*nu[2]-nu[1]**2,
            'rational_111_anchor_example':{'degree':111,'sign_changes':barrier['sign_changes'],
                'balance_status':barrier['status'],'lower_multiplier':barrier['lower_multiplier'],
                'is_actual_xi_root_data':False},
            'new_actual_xi_numerical_claim':False,'rh_proved':False,'canonical_admission':False}


if __name__=='__main__':
    import json,sys
    try:
        text=json.dumps(report(),default=str,sort_keys=True,indent=2)
        if len(text)>250000:raise ValueError('report budget')
        print(text)
        print('DEFLATION_EXACT_PASS: root barrier and complete finite Schur countermodels; NOT RH.')
    except Exception as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr);raise SystemExit(1) from exc
