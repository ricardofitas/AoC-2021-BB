"""Python solvers and a thin interface to the native kernels."""

import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .exact import lanternfish, polymer

ROOT = Path(__file__).resolve().parents[1]
NATIVE_DAYS = {4, 5, 9, 11, 12, 15, 17}


def diagnostic(path):
    raw = path.read_bytes().replace(b"\r", b"").rstrip(b"\n")
    width = raw.find(b"\n")
    if width < 0:
        width = len(raw)
    raw += b"\n"
    if width == 0 or len(raw) % (width + 1):
        raise ValueError("Invalid diagnostic rows")
    data = np.frombuffer(raw, dtype=np.uint8).reshape(-1, width + 1)[:, :width]
    if not np.all((data == 48) | (data == 49)):
        raise ValueError("Diagnostic input must contain binary digits")
    ones = np.sum(data == 49, axis=0)
    gamma = int("".join("1" if 2 * n >= len(data) else "0" for n in ones), 2)

    def rating(oxygen):
        candidates = np.arange(len(data))
        for col in range(width):
            if len(candidates) == 1:
                break
            values = data[candidates, col]
            ones = int(np.count_nonzero(values == 49))
            zeros = len(candidates) - ones
            # Do not choose an absent bit, even for duplicate/degenerate rows.
            bit = (
                1
                if zeros == 0
                else 0
                if ones == 0
                else int(ones >= zeros)
                if oxygen
                else int(ones < zeros)
            )
            candidates = candidates[values == 48 + bit]
        return int(bytes(data[candidates[0]]), 2)

    return gamma * (gamma ^ ((1 << width) - 1)), rating(True) * rating(False)


def crabs(path):
    positions = np.fromstring(path.read_text(), dtype=np.int64, sep=",")
    if not positions.size or np.any(positions < 0):
        raise ValueError("Expected nonnegative crab positions")
    # Python integers keep the squared-distance sum exact for arbitrary large totals.
    values = list(map(int, positions))
    n = len(values)
    median = int(np.partition(positions, n // 2)[n // 2])
    p1 = sum(abs(x - median) for x in values)
    mean_floor = sum(values) // n

    def fuel(target):
        return sum((d := abs(x - target)) * (d + 1) // 2 for x in values)

    return p1, min(fuel(mean_floor), fuel(mean_floor + 1))


def displays(path):
    p1 = p2 = 0
    for line in path.read_text().splitlines():
        patterns, output = line.split(" | ")
        masks = [sum(1 << (ord(c) - 97) for c in word) for word in patterns.split()]
        by_length = {n: [m for m in masks if m.bit_count() == n] for n in range(2, 8)}
        one, four, seven, eight = (by_length[n][0] for n in (2, 4, 3, 7))
        digits = {one: 1, four: 4, seven: 7, eight: 8}
        six = next(m for m in by_length[6] if m & one != one)
        for mask in by_length[6]:
            digits[mask] = 6 if mask == six else 9 if mask & four == four else 0
        for mask in by_length[5]:
            digits[mask] = 3 if mask & one == one else 5 if mask & six == mask else 2
        value = 0
        for word in output.split():
            p1 += len(word) in (2, 3, 4, 7)
            mask = sum(1 << (ord(c) - 97) for c in word)
            value = value * 10 + digits[mask]
        p2 += value
    return p1, p2


def brackets(path):
    opening = {40: 41, 91: 93, 123: 125, 60: 62}
    corrupt = {41: 3, 93: 57, 125: 1197, 62: 25137}
    completion = {41: 1, 93: 2, 125: 3, 62: 4}
    p1 = 0
    scores = []
    with path.open("rb") as stream:
        for line in stream:
            stack = []
            for c in line.strip():
                if c in opening:
                    stack.append(opening[c])
                elif c not in corrupt:
                    raise ValueError("Invalid bracket character")
                elif not stack or stack.pop() != c:
                    p1 += corrupt[c]
                    break
            else:
                if stack:
                    score = 0
                    for c in reversed(stack):
                        score = score * 5 + completion[c]
                    scores.append(score)
    if not scores:
        raise ValueError("No incomplete lines for the completion median")
    scores.sort()
    return p1, scores[len(scores) // 2]


def solve(case, data_dir, binary=ROOT / "build/solver"):
    day = case["day"]
    path = data_dir / case["file"].removesuffix(".xz") if "file" in case else None
    if day in NATIVE_DAYS:
        if day == 17:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as target:
                target.write(" ".join(map(str, case["target"])))
                target.flush()
                result = subprocess.run(
                    [str(binary), str(day), target.name],
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                )
        else:
            result = subprocess.run(
                [str(binary), str(day), str(path)], check=True, text=True, stdout=subprocess.PIPE
            )
        a, b = result.stdout.split()
        return {"part1": a, "part2": b}
    if day == 6:
        return {"value": str(lanternfish(case["initial"], case["steps"]))}
    if day == 14:
        return {"value": str(polymer(path.read_text(), case["steps"]))}
    functions = {3: diagnostic, 7: crabs, 8: displays, 10: brackets}
    a, b = functions[day](path)
    return {"part1": str(a), "part2": str(b)}
