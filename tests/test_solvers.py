"""Small independent oracles exercise the algorithms used for the large cases."""

import heapq
import random
import subprocess
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from aocbb.exact import convolution, lanternfish, polymer
from aocbb.solvers import ROOT, brackets, crabs, diagnostic, displays


def native(day, text, tiles=None):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".in") as stream:
        stream.write(text)
        stream.flush()
        command = [str(ROOT / "build/solver"), str(day), stream.name]
        if tiles is not None:
            command.append(str(tiles))
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    return tuple(map(int, result.stdout.split()))


def python_solver(function, text):
    with tempfile.NamedTemporaryFile(mode="w") as stream:
        stream.write(text)
        stream.flush()
        return function(Path(stream.name))


class ExactArithmeticTests(unittest.TestCase):
    def test_signed_convolution(self):
        rng = random.Random(81)
        for _ in range(100):
            a = [rng.randrange(-(10**30), 10**30) for _ in range(rng.randrange(1, 20))]
            b = [rng.randrange(-(10**30), 10**30) for _ in range(rng.randrange(1, 20))]
            expected = [0] * (len(a) + len(b) - 1)
            for i, x in enumerate(a):
                for j, y in enumerate(b):
                    expected[i + j] += x * y
            self.assertEqual(convolution(a, b), expected)

    def test_fish_against_simulation(self):
        rng = random.Random(62)
        for steps in (0, 1, 2, 7, 8, 9, 18, 80, 256, 1000):
            initial = [rng.randrange(9) for _ in range(12)]
            counts = Counter(initial)
            for _ in range(steps):
                updated = Counter({i - 1: n for i, n in counts.items() if i})
                updated[6] += counts[0]
                updated[8] += counts[0]
                counts = updated
            self.assertEqual(lanternfish(initial, steps), sum(counts.values()))

    def test_polymer_against_literal_expansion(self):
        rng = random.Random(142)
        for _ in range(12):
            alphabet = "ABC"
            template = "".join(rng.choice(alphabet) for _ in range(5))
            rules = {
                a + b: rng.choice(alphabet)
                for a in alphabet
                for b in alphabet
                if rng.random() < 0.8
            }
            text = template + "\n\n" + "\n".join(f"{a} -> {b}" for a, b in rules.items())
            for steps in (0, 1, 4, 9):
                current = template
                for _ in range(steps):
                    current = (
                        "".join(a + rules.get(a + b, "") for a, b in zip(current, current[1:]))
                        + current[-1]
                    )
                counts = Counter(current)
                self.assertEqual(polymer(text, steps), max(counts.values()) - min(counts.values()))
        self.assertEqual(polymer("A\n", 1000000), 0)


class NativeTests(unittest.TestCase):
    def test_bingo(self):
        # Two 2x2 boards, with distinct first and last winning draw times.
        self.assertEqual(native(4, "1,2,3,4,5,6,7,8\n\n1 2\n7 8\n\n3 4\n5 6\n"), (30, 44))

    def test_vents_dense_and_sparse_against_point_counting(self):
        rng = random.Random(521)
        for trial in range(30):
            lines = []
            counts = [Counter(), Counter()]
            for _ in range(40):
                x, y = rng.randrange(15), rng.randrange(15)
                dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
                length = rng.randrange(
                    min(15 - x if dx else 15, 15 - y if dy > 0 else y + 1 if dy < 0 else 15)
                )
                u, v = x + dx * length, y + dy * length
                lines.append((x, y, u, v))
                for k in range(length + 1):
                    p = (x + dx * k, y + dy * k)
                    counts[1][p] += 1
                    if x == u or y == v:
                        counts[0][p] += 1
            expected = tuple(sum(n >= 2 for n in c.values()) for c in counts)
            for offset in (0, 10000000):
                text = "\n".join(
                    f"{x + offset},{y + offset} -> {u + offset},{v + offset}"
                    for x, y, u, v in lines
                )
                self.assertEqual(native(5, text), expected, f"trial {trial}, offset {offset}")

    def test_basins_multiple_minima_counted_once(self):
        # Connected non-9 components have sizes 3, 3, 1, 1; the first two each have two minima.
        self.assertEqual(native(9, "01099\n99999\n01099\n99999\n09990\n"), (6, 9))

    def test_octopi_against_simulation(self):
        rng = random.Random(111)
        for _ in range(8):
            a = [[rng.randrange(10) for _ in range(3)] for _ in range(2)]
            text = "\n".join("".join(map(str, row)) for row in a)
            total = sync = 0
            for step in range(1, 3000):
                for row in a:
                    for x in range(3):
                        row[x] += 1
                flashed = set()
                while True:
                    found = [
                        (y, x)
                        for y in range(2)
                        for x in range(3)
                        if a[y][x] > 9 and (y, x) not in flashed
                    ]
                    if not found:
                        break
                    for y, x in found:
                        flashed.add((y, x))
                        for yy in range(max(0, y - 1), min(2, y + 2)):
                            for xx in range(max(0, x - 1), min(3, x + 2)):
                                if (yy, xx) != (y, x):
                                    a[yy][xx] += 1
                for y, x in flashed:
                    a[y][x] = 0
                if step <= 100:
                    total += len(flashed)
                if len(flashed) == 6 and not sync:
                    sync = step
                if step >= 100 and sync:
                    break
            if sync:
                self.assertEqual(native(11, text), (total, sync))

    def test_caves_against_path_enumeration(self):
        rng = random.Random(1224)
        for _ in range(30):
            names = ["start", "end", "a", "b", "c", "d", "A", "B"]
            edges = [("start", "a"), ("a", "end")]
            for i, a in enumerate(names):
                for b in names[i + 1 :]:
                    if a.isupper() and b.isupper():
                        continue
                    if rng.random() < 0.2:
                        edges.append((a, b))
            edges = sorted(set(edges))
            adj = defaultdict(list)
            for a, b in edges:
                adj[a].append(b)
                adj[b].append(a)

            def visit(node, visited, extra):
                if node == "end":
                    return 1
                result = 0
                for dest in adj[node]:
                    if dest == "start":
                        continue
                    if dest.isupper():
                        result += visit(dest, visited, extra)
                    elif dest not in visited:
                        result += visit(dest, visited | {dest}, extra)
                    elif extra:
                        result += visit(dest, visited, False)
                return result

            expected = (visit("start", {"start"}, False), visit("start", {"start"}, True))
            self.assertEqual(native(12, "\n".join(a + "-" + b for a, b in edges)), expected)

    def test_pathfinding_against_heap_dijkstra(self):
        rng = random.Random(1525)
        for _ in range(15):
            h, w = rng.randrange(1, 8), rng.randrange(1, 8)
            a = [[rng.randrange(1, 10) for _ in range(w)] for _ in range(h)]
            text = "\n".join("".join(map(str, row)) for row in a)
            expected = []
            for tiles in (1, 5):
                hh, ww = h * tiles, w * tiles
                queue = [(0, 0, 0)]
                dist = {(0, 0): 0}
                while queue:
                    d, y, x = heapq.heappop(queue)
                    if d != dist[y, x]:
                        continue
                    if (y, x) == (hh - 1, ww - 1):
                        expected.append(d)
                        break
                    for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                        if 0 <= yy < hh and 0 <= xx < ww:
                            dd = d + (a[yy % h][xx % w] + yy // h + xx // w - 1) % 9 + 1
                            if dd < dist.get((yy, xx), 10**20):
                                dist[yy, xx] = dd
                                heapq.heappush(queue, (dd, yy, xx))
            self.assertEqual(native(15, text), tuple(expected))

    def test_projectiles_against_velocity_enumeration(self):
        rng = random.Random(173)
        for _ in range(30):
            xmin, xmax = sorted(rng.sample(range(1, 25), 2))
            ymin, ymax = sorted(rng.sample(range(-20, 0), 2))
            velocities = set()
            for vx in range(xmax + 1):
                for vy in range(ymin, -ymin):
                    x = y = 0
                    dx = vx
                    dy = vy
                    for t in range(-2 * ymin):
                        x += dx
                        y += dy
                        dx = max(0, dx - 1)
                        dy -= 1
                        if xmin <= x <= xmax and ymin <= y <= ymax:
                            velocities.add((vx, vy))
                            break
            height = max((vy * (vy + 1) // 2 if vy > 0 else 0 for vx, vy in velocities), default=0)
            expected = (height, len(velocities))
            self.assertEqual(native(17, f"{xmin} {xmax} {ymin} {ymax}"), expected)
            self.assertEqual(native(17, f"{-xmax} {-xmin} {ymin} {ymax}"), expected)


class PythonTests(unittest.TestCase):
    def test_diagnostic_arbitrary_width(self):
        self.assertEqual(python_solver(diagnostic, "10\n11\n01\n"), (0, 3))
        self.assertEqual(
            python_solver(diagnostic, "1" * 100 + "\n" + "1" * 100 + "\n"),
            (0, ((1 << 100) - 1) ** 2),
        )

    def test_crabs_against_exhaustive_targets(self):
        rng = random.Random(7)
        for _ in range(25):
            a = [rng.randrange(100) for _ in range(30)]
            expected = (
                min(sum(abs(x - t) for x in a) for t in range(100)),
                min(sum((d := abs(x - t)) * (d + 1) // 2 for x in a) for t in range(100)),
            )
            self.assertEqual(python_solver(crabs, ",".join(map(str, a))), expected)

    def test_display_random_permutations(self):
        patterns = [
            "abcefg",
            "cf",
            "acdeg",
            "acdfg",
            "bcdf",
            "abdfg",
            "abdefg",
            "acf",
            "abcdefg",
            "abcdfg",
        ]
        rng = random.Random(8)
        for _ in range(30):
            shuffled = rng.sample(list("abcdefg"), 7)
            mapping = dict(zip("abcdefg", shuffled))

            def encode(s):
                return "".join(mapping[c] for c in s)

            digits = [rng.randrange(10) for _ in range(4)]
            text = (
                " ".join(encode(s) for s in rng.sample(patterns, 10))
                + " | "
                + " ".join(encode(patterns[d]) for d in digits)
            )
            self.assertEqual(
                python_solver(displays, text),
                (sum(d in (1, 4, 7, 8) for d in digits), int("".join(map(str, digits)))),
            )

    def test_brackets_big_integer_and_complete_lines(self):
        self.assertEqual(
            python_solver(brackets, "([)]\n()\n" + "(" * 200 + "\n"), (3, (5**200 - 1) // 4)
        )


if __name__ == "__main__":
    unittest.main()
