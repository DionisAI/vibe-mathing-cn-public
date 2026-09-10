#!/usr/bin/env python3
"""Exact finite sign-block compression, not a validator of infinite xi input.

Zero coefficients are removed before counting sign changes. Ordered disjoint
supports, exact positive weights and explicit input budgets are mandatory.
"""
from fractions import Fraction as F
from itertools import product
from math import prod

MAX_TERMS = 128
MAX_BLOCKS = 16
MAX_EXPONENT = 1000000
MAX_BITS = 2048
MAX_EXPANSION_PAIRS = 4096


def rational(x):
    """Accept only bounded exact integers and Fractions."""
    if type(x) not in (int, F):
        raise ValueError('exact rational required')
    x = F(x)
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ValueError('input bit budget exceeded')
    return x


def sign_blocks(terms):
    """Return ordered positive-weight supports and their signs; reject zero p."""
    if not isinstance(terms, (tuple, list)) or not 1 <= len(terms) <= MAX_TERMS:
        raise ValueError('term budget exceeded or empty input')
    groups, signs, previous = [], [], -1
    for item in terms:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError('expected exponent/coefficient pair')
        e, c = item
        if type(e) is not int or not previous < e <= MAX_EXPONENT:
            raise ValueError('exponents must be increasing bounded nonnegative integers')
        previous = e
        c = rational(c)
        if c == 0:
            continue
        s = 1 if c > 0 else -1
        if not signs or signs[-1] != s:
            groups.append([]); signs.append(s)
        groups[-1].append((e, abs(c)))
    if not groups:
        raise ValueError('zero polynomial is excluded from strict positivity')
    return tuple(tuple(g) for g in groups), tuple(signs)


def validate_blocks(blocks):
    """Check nonempty, ordered disjoint positive-weight supports."""
    if not isinstance(blocks, (tuple, list)) or not 1 <= len(blocks) <= MAX_BLOCKS:
        raise ValueError('block budget exceeded')
    total, previous, out = 0, -1, []
    for block in blocks:
        if not isinstance(block, (tuple, list)) or not block:
            raise ValueError('empty support')
        b = []
        for item in block:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise ValueError('expected index/weight pair')
            i, w = item
            if type(i) is not int or not previous < i <= MAX_EXPONENT:
                raise ValueError('supports must be globally ordered and disjoint')
            previous = i
            w = rational(w)
            if w <= 0:
                raise ValueError('strictly positive weights required')
            b.append((i, w)); total += 1
        out.append(tuple(b))
    if total > MAX_TERMS:
        raise ValueError('term budget exceeded')
    return tuple(out)


def compress(kernel, row_blocks, column_blocks=None):
    """Compute the finite mixed compression; kernel values must be exact."""
    rows = validate_blocks(row_blocks)
    cols = rows if column_blocks is None else validate_blocks(column_blocks)
    return [[sum((w*v*rational(kernel(i, j)) for i, w in a for j, v in b), F(0))
             for b in cols] for a in rows]


def determinant(matrix):
    """Bounded rational Gaussian elimination with exact swaps and singularity."""
    n = len(matrix)
    if not 0 <= n <= MAX_BLOCKS or any(len(r) != n for r in matrix):
        raise ValueError('bounded square matrix required')
    a = [[rational(x) for x in r] for r in matrix]
    ans = F(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]; ans = -ans
        p = a[j][j]; ans *= p
        for i in range(j+1, n):
            t = a[i][j]/p
            for k in range(j+1, n):
                a[i][k] -= t*a[j][k]
    return ans


def expanded_determinant(kernel, row_blocks, column_blocks=None):
    """Independent multilinear expansion; exponential finite oracle only."""
    rows = validate_blocks(row_blocks)
    cols = rows if column_blocks is None else validate_blocks(column_blocks)
    if len(rows) != len(cols):
        raise ValueError('square compression required')
    count = prod(map(len, rows))*prod(map(len, cols))
    if count > MAX_EXPANSION_PAIRS:
        raise ValueError('expansion-pair budget exceeded')
    value = F(0); minimum = None
    for ri in product(*rows):
        for cj in product(*cols):
            d = determinant([[kernel(i, j) for j, _ in cj] for i, _ in ri])
            w = prod(x[1] for x in ri)*prod(x[1] for x in cj)
            value += w*d
            minimum = d if minimum is None else min(minimum, d)
    return {'determinant': value, 'selection_pairs': count, 'minimum_selected_minor': minimum}


def quadratic(matrix, vector):
    """Evaluate a bounded exact quadratic form without a positivity inference."""
    n = len(vector)
    if not 1 <= n <= MAX_TERMS or len(matrix) != n or any(len(r) != n for r in matrix):
        raise ValueError('incompatible bounded dimensions')
    v = list(map(rational, vector))
    return sum((v[i]*rational(matrix[i][j])*v[j] for i in range(n) for j in range(n)), F(0))


def classify_direction(terms, certified_order=10):
    """Conditional screening rule only: never assert actual-xi input is verified."""
    if type(certified_order) is not int or not 1 <= certified_order <= MAX_BLOCKS:
        raise ValueError('invalid supplied order')
    blocks, signs = sign_blocks(terms)
    return {'nonzero_terms': sum(map(len, blocks)), 'sign_changes': len(blocks)-1,
            'covered_if_kernel_is_strict_TP_order': len(blocks) <= certified_order,
            'required_kernel_order': len(blocks), 'supplied_order': certified_order,
            'kernel_input_verified_here': False}
