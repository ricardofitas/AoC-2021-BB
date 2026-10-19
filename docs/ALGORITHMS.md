# Algorithms and correctness

These implementations target every case in Tomasz Kramkowski's [AoC 2021 Big Inputs collection](https://kramkow.ski/project/aoc2021-bigboys.html). Their answers are computed from the downloaded inputs. Published answers are used only by the verification layer; they are not embedded in the solving algorithms.

## Day 3 — Binary diagnostic

NumPy counts each bit column in the million-row array. Oxygen and CO2 ratings repeatedly filter row indices by the required bit, with the specified tie rules. The final arithmetic uses Python integers, including the product of two 100-bit numbers. An absent bit is never selected in a degenerate candidate set. Time is linear in the number of input characters plus the filtering work; memory is linear in the input size.

## Day 4 — Giant bingo boards

Map each drawn number to its first draw time. A row or column completes at the maximum draw time of its cells; a board wins at the minimum of those row/column maxima. Sum the cells whose draw times are later than the winning time and multiply by the winning draw. This avoids replaying thousands of draws over thousands of boards. Missing drawn values have an infinite draw time. Simultaneous first wins use the first board in input order; simultaneous last wins use the last. The published cases have the expected unambiguous outcomes.

## Day 5 — Huge vent fields

For domains up to 100 million cells, a byte per cell stores the coverage count saturated at two.

For the 10,000,000 × 10,000,000 domain, allocating the field or walking every point is unnecessary. The input would require 138,436,065,110 point visits with a direct approach.

1. Classify vents as horizontal, vertical, ascending diagonal, or descending diagonal.
2. On each supporting line, sweep interval endpoints into disjoint inclusive integer intervals, labelled with coverage one or at least two.
3. Initially count every point in intervals with coverage at least two.
4. Find intersections between intervals of different orientations. Opposite diagonals intersect on the integer lattice only when their offset difference is even.
5. Group equal intersection coordinates. If `d` distinct orientations already contributed double coverage at that point, add `1 - d` to the total.

Every cross-orientation intersection must count exactly once. The initial total counts it `d` times, so the correction is exact even for triple/quadruple intersections and overlapping collinear vents. Part 1 uses only horizontal and vertical orientations; part 2 includes all four.

With `M_i` merged intervals in each orientation and `I` reported pair intersections, the sparse method takes `O(sum(M_i*M_j) + I log I)` time and `O(sum(M_i) + I)` memory. This is not an algorithm with guaranteed subquadratic complexity in the number of segments. Coordinates must be nonnegative and less than `2^30`; both coordinates and a four-bit coverage mask then fit in a 64-bit record.

## Day 6 — Tens of millions of lanternfish cycles

The population sequence satisfies

```text
F(n + 9) = F(n + 2) + F(n).
```

Therefore compute `x^N mod (x^9 - x^2 - 1)` by binary exponentiation and take the dot product of its nine coefficients with the first nine population totals. GMP supplies arbitrary-precision integers. No floating-point estimate or decimal truncation is used.

The complete largest result has 2,539,031 decimal digits. Independent 9 × 9 transition-matrix exponentiation checks the result modulo 1,000,003, 1,000,033, and `2^64`.

## Day 7 — Crab alignment

The median minimizes total absolute distance. The minimum triangular-distance cost lies at either the floor or ceiling of the arithmetic mean, so evaluate both. All sums use arbitrary-precision Python integers, including squared distances. Selection and evaluation are linear in the number of crabs.

## Day 8 — Seven-segment displays

Represent each pattern by a seven-bit mask. Unique lengths identify 1, 4, 7, and 8. Inclusion relationships distinguish the remaining length-five and length-six digits. Each entry is independent, and the algorithm is linear in the number of entries.

## Day 9 — Basins and the author's broken input

Risk is calculated by comparing each cell with its orthogonal neighbors. Basins are connected components of cells below nine; breadth-first traversal visits each cell at most once.

`9-4096-2` is explicitly labelled **broken** by the author because components can contain multiple local minima. We count each connected basin once, matching the author's primary part-2 answer, `4971158490375`. The alternative `5292585633483` counts duplicate basins and is deliberately not the convention used here. This extension is documented rather than pretending that the input satisfies the original unique-basin assumptions.

## Day 10 — Very long bracket lines

A stack stores expected closing brackets. The first mismatch contributes the corruption score. For an incomplete, uncorrupted line, pop the remaining closers and accumulate the base-five completion score. Completely balanced lines are excluded from the completion median. Python integers preserve every digit of the long scores.

## Day 11 — Million-cell octopus simulation

Use a flat byte grid surrounded by sentinel cells. Increment every interior cell, queue a cell exactly when its energy reaches ten, and propagate each flash to eight neighbors. A flashed cell is set to zero and cannot flash again during the same step. Continue until both the 100-step count and the first synchronization have been found. A one-million-step guard reports an error instead of silently assuming that synchronization always exists.

## Day 12 — Weighted subset dynamic programming

The published cave graphs have no big-to-big edges. Eliminate each big cave: an edge between two small caves receives a multiplicity equal to the number of possible one-big-cave routes, plus any direct edge. Preserve self-return edges, which consume the optional revisit.

For every visited-small-cave subset `S` and last cave `u`, store two counts:

- `once[S,u]`: no small cave has been revisited;
- `twice[S,u]`: the permitted single revisit has been consumed.

First transfer `once` to `twice` for destinations already in `S`. Then extend both states to previously unvisited caves, multiplying by edge multiplicity. Edges to `end` contribute to the answer, while returning to `start` is forbidden.

Process subsets by cardinality and retain only the current and next layers. Packed subset ranks and population counts avoid hash-table overhead. Unsigned 128-bit integers accommodate the published path counts, including `33501351222065201672`, which exceeds unsigned 64-bit capacity.

The implementation supports up to 24 ordinary small caves. Big-to-big edges are rejected because they require separate analysis of infinite routes. It is not a general unbounded-precision cave counter for arbitrary graph sizes. Complexity remains exponential in the number of small caves; the layered representation reduces peak memory substantially.

## Day 14 — Million-step polymer growth

Track adjacent-pair counts. Pair insertion is a sparse integer linear transformation `T`; no-rule pairs map to themselves. Close the set of pairs under the transformation, then calculate its characteristic polynomial exactly with SymPy.

Cayley–Hamilton gives a polynomial representation of `T^N` of degree below the number of reachable pairs. Compute that polynomial by modular exponentiation and apply it to the initial pair-count vector. Count the first character of each pair and add the final character of the template once. The difference between the largest and smallest nonzero character counts is the exact answer.

To accelerate polynomial multiplication, encode signed coefficients as balanced digits of a power-of-two radix. The radix is greater than twice an upper bound on any convolution coefficient. A single GMP integer multiplication therefore computes the convolution, and balanced digit extraction recovers each coefficient without overlap or ambiguity. This same helper accelerates day 6.

An independent matrix-exponentiation implementation validates **every final pair count** modulo 1,000,003, 1,000,033, and `2^64`. For the two small moduli, each matrix dot product fits in `uint64`; for `2^64`, unsigned overflow is exactly the intended modular arithmetic.

## Day 15 — A 2.5-billion-cell shortest path

Run exact Dijkstra with a circular array of sixteen distance buckets (Dial's algorithm). Risks are positive integers from one to nine. At distance `d`, every unsettled candidate is at most nine units ahead, so a four-bit distance residue is enough to compare active tentative distances. Separate byte values represent unseen and settled states. Stale queue entries are ignored.

The expanded risk grid and queue-state grid use one byte each per cell, plus sentinel borders. At 50,000 × 50,000, these two arrays occupy approximately 4.66 GiB. The original input and bucket vectors require additional memory. A 32-bit node index is sufficient for this collection; larger expanded grids are rejected.

No monotone-path assumption, heuristic estimate, sampled subgrid, or precomputed answer replaces the shortest-path calculation. Both the original and fivefold-expanded maps are solved. The runtime is linear in the vertex/edge count for bounded integer weights, although traversing billions of cells remains substantial work.

## Day 17 — Count a union of velocity rectangles

For each possible hit time `t`, derive integer intervals of admissible initial velocities from

```text
y(t) = t*vy - t*(t-1)/2
x(t) = t*vx - t*(t-1)/2       while vx >= t
x(t) = vx*(vx+1)/2            after horizontal motion stops.
```

A target wholly below the origin has a hit-time upper bound of `-2*ymin`. Each time produces at most two rectangles of initial `(vx, vy)` values. Count their union using an x-coordinate event sweep and a segment tree storing covered y-interval length. This deduplicates trajectories that hit at multiple times without enumerating billions of velocity pairs. The largest admissible `vy` determines the maximum height.

The implementation handles the collection's positive-x, negative-y targets, and mirrored negative-x targets. It rejects targets crossing the vertical axis or not wholly below the origin, whose bounds and possible infinite cases require a different treatment.

## What the validation establishes

The test suite compares algorithms to separately written small-case oracles, including randomized point counting, exhaustive trajectories, path enumeration, heap Dijkstra, direct population simulation, literal polymer expansion, and signed polynomial multiplication.

The full-size run compares every value with all information published by the dataset author. For days 6 and 14, those publications contain fingerprints rather than full decimal answers: digit counts, leading/trailing digits, and (for day 14) residues. Passing those checks is not the same as comparing every digit with an external reference. Independent modular checks provide additional evidence, while exact arithmetic and the algorithm derivations explain how the full answers were produced.
