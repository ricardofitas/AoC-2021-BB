"""Exact recurrence acceleration using GMP and balanced Kronecker substitution."""

from collections import Counter

import numpy as np
from gmpy2 import mpz


def convolution(a, b):
    """Multiply signed integer polynomials with one packed GMP multiplication.

    The radix exceeds twice the absolute bound on any convolution coefficient,
    so balanced digit extraction is unambiguous, including negative carries.
    """
    bound = min(len(a), len(b)) * max(map(abs, a), default=0) * max(map(abs, b), default=0)
    bits = max(2, int(bound).bit_length() + 2)
    radix = mpz(1) << bits
    mask = radix - 1
    half = radix >> 1

    def pack(values):
        result = mpz(0)
        for value in reversed(values):
            result = (result << bits) + value
        return result

    packed = pack(a) * pack(b)
    result = []
    for _ in range(len(a) + len(b) - 1):
        digit = packed & mask
        if digit >= half:
            digit -= radix
        result.append(digit)
        packed = (packed - digit) >> bits
    assert packed == 0
    return result


def power_x(exponent, reduction):
    """Return x**exponent modulo x**k - sum(reduction[i] * x**i)."""
    if exponent < 0:
        raise ValueError("Negative iteration count")
    k = len(reduction)
    nonzero = [(i, mpz(c)) for i, c in enumerate(reduction) if c]

    def multiply(a, b):
        values = convolution(a, b)
        for j in range(len(values) - 1, k - 1, -1):
            c = values[j]
            if c:
                for i, r in nonzero:
                    values[j - k + i] += c * r
        return values[:k]

    result = [mpz(1)] + [mpz(0)] * (k - 1)
    base = ([mpz(0), mpz(1)] + [mpz(0)] * (k - 2)) if k > 1 else [mpz(reduction[0])]
    while exponent:
        if exponent & 1:
            result = multiply(result, base)
        exponent >>= 1
        if exponent:
            base = multiply(base, base)
    return result


def modular_state(matrix, initial, steps, modulus):
    """Independent binary matrix exponentiation, without polynomial reduction."""
    matrix = np.array(matrix, dtype=np.uint64)
    state = np.array(initial, dtype=np.uint64)
    wrap = modulus == 2**64
    if not wrap:
        matrix %= np.uint64(modulus)
        state %= np.uint64(modulus)
    while steps:
        if steps & 1:
            state = matrix @ state
            if not wrap:
                state %= np.uint64(modulus)
        steps >>= 1
        if steps:
            matrix = matrix @ matrix
            if not wrap:
                matrix %= np.uint64(modulus)
    return [int(n) for n in state]


def lanternfish(initial, steps):
    if any(t < 0 or t > 8 for t in initial):
        raise ValueError("Fish timers must be 0..8")
    state = [mpz(0)] * 9
    for timer in initial:
        state[timer] += 1
    sequence = []
    for _ in range(9):
        sequence.append(sum(state))
        zero = state[0]
        state = state[1:] + [zero]
        state[6] += zero
    coefficients = power_x(steps, [1, 0, 1, 0, 0, 0, 0, 0, 0])
    answer = sum((a * b for a, b in zip(coefficients, sequence)), mpz(0))
    matrix = [[0] * 9 for _ in range(9)]
    for i in range(8):
        matrix[i][i + 1] = 1
    matrix[6][0] = matrix[8][0] = 1
    initial_counts = [initial.count(i) for i in range(9)]
    for modulus in (1000003, 1000033, 2**64):
        check = sum(modular_state(matrix, initial_counts, steps, modulus)) % modulus
        if answer % modulus != check:
            raise ArithmeticError(f"Independent fish check failed modulo {modulus}")
    return answer


def polymer(text, steps):
    from sympy import Matrix

    lines = text.strip().splitlines()
    template = lines[0].strip()
    if not template:
        raise ValueError("Empty polymer template")
    rules = dict(line.split(" -> ") for line in lines[1:] if line.strip())
    # Close the pair set under the actual transition, including pairs without rules.
    pairs = set(a + b for a, b in zip(template, template[1:]))
    pending = list(pairs)
    while pending:
        pair = pending.pop()
        if pair in rules:
            middle = rules[pair]
            if len(pair) != 2 or len(middle) != 1:
                raise ValueError("Invalid insertion rule")
            for child in (pair[0] + middle, middle + pair[1]):
                if child not in pairs:
                    pairs.add(child)
                    pending.append(child)
    pairs = sorted(pairs)
    if not pairs:
        return mpz(0)
    index = {pair: i for i, pair in enumerate(pairs)}
    k = len(pairs)
    matrix = [[0] * k for _ in range(k)]
    for j, pair in enumerate(pairs):
        children = (pair[0] + rules[pair], rules[pair] + pair[1]) if pair in rules else (pair,)
        for child in children:
            matrix[index[child]][j] += 1
    # Cayley-Hamilton makes this exact for any nonnegative iteration count.
    characteristic = list(map(int, Matrix(matrix).charpoly().all_coeffs()))
    reduction = [-c for c in reversed(characteristic[1:])]
    coefficients = power_x(steps, reduction)
    counts = Counter(a + b for a, b in zip(template, template[1:]))
    initial = [counts[p] for p in pairs]
    state = list(initial)
    final = [mpz(0)] * k
    transitions = [[(i, matrix[i][j]) for i in range(k) if matrix[i][j]] for j in range(k)]
    for coefficient in coefficients:
        for i in range(k):
            final[i] += coefficient * state[i]
        new = [0] * k
        for j, value in enumerate(state):
            for i, multiplicity in transitions[j]:
                new[i] += multiplicity * value
        state = new
    if any(n < 0 for n in final):
        raise ArithmeticError("Negative exact pair count")
    for modulus in (1000003, 1000033, 2**64):
        check = modular_state(matrix, initial, steps, modulus)
        if any(n % modulus != r for n, r in zip(final, check)):
            raise ArithmeticError(f"Independent polymer check failed modulo {modulus}")
    letters = Counter({template[-1]: mpz(1)})
    for pair, value in zip(pairs, final):
        letters[pair[0]] += value
    positive = [value for value in letters.values() if value]
    return max(positive) - min(positive)
