# Advent of Code 2021 — Big Inputs

Exact solutions for **all 27 published cases across 13 puzzle days** in Tomasz Kramkowski's [AOC 2021 Big Inputs (Big Boys)](https://kramkow.ski/project/aoc2021-bigboys.html) collection.

This repository contains the solving algorithms, all **49 complete computed answers**, reproducible verification tools, independent small-case tests, and measured full-size results. Everything is in English.

- [Full-size results and answer links](reports/RESULTS.md)
- [Algorithm explanations and correctness notes](docs/ALGORITHMS.md)
- [Machine-readable verification report](reports/verification.json)
- [Dataset catalogue and published reference checks](cases.json)
- [Complete answer files](answers/)

## Coverage

| Day | Cases | Main scaling challenge | Method |
|---|---:|---|---|
| 3 | 1 | 1,000,001 rows of 100 bits | Vectorized bit counts; arbitrary-precision products |
| 4 | 2 | Up to 3,600 bingo boards of 30 × 30 | Compute winning draw times directly |
| 5 | 3 | 50,000 vents over a 10,000,000 × 10,000,000 field | Collinear interval merging and exact lattice intersections |
| 6 | 2 | Up to 67,108,864 cycles; 2,539,031-digit answer | Polynomial recurrence exponentiation with GMP |
| 7 | 1 | 1,000,000 crabs | Median and neighboring integer means |
| 8 | 1 | 100,000 scrambled displays | Seven-bit masks |
| 9 | 2 | 4,096 × 4,096 maps | Connected-component traversal |
| 10 | 2 | Up to roughly 92 MiB of bracket text | Stack parsing and arbitrary-precision scoring |
| 11 | 2 | Up to 1,000 × 1,000 octopi | Flat byte grid and flash queue |
| 12 | 4 | Up to 24 small caves; counts beyond 64 bits | Weighted subset DP with two cardinality layers |
| 14 | 3 | Up to 1,000,000 insertion steps | Exact characteristic-polynomial acceleration |
| 15 | 2 | Up to 50,000 × 50,000 after expansion | Exact bucketed Dijkstra with compact state |
| 17 | 2 | More than 12 billion valid velocity pairs | Union of velocity rectangles |

The collection does not provide Big Inputs for the other 2021 days. “All” refers to this named collection, including its inline day-6/day-17 cases and its explicitly broken day-9 dataset.

## Reproduce the results

Use Linux or WSL with Python 3.12, a C++20 compiler (GCC or Clang), and Make. **Allow at least 8 GiB of RAM** for the largest pathfinding case and approximately 1 GiB of disk space for downloaded/decompressed datasets and outputs. No GPU is needed.

```bash
git clone https://github.com/ricardofitas/AoC-2021-BB.git
cd AoC-2021-BB
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make test
make download
make verify
python scripts/summarize.py
```

Dependencies are pinned to the versions used for the recorded run. `make download` fetches the author's synthetic files, verifies their recorded SHA-256 checksums, decompresses them, and verifies the decompressed-file checksums as well. Inputs are excluded from Git.

`make verify` runs each case in an isolated process, saves every decimal answer under `answers/`, checks the published references, and checkpoints `reports/verification.json` after each case. A failed check exits with an error.

List cases or run a single one:

```bash
python -m aocbb list
python -m aocbb run --case 6-67108864 --report reports/single-case.json
python -m aocbb run --case 15-10000 --report reports/single-case.json
```

Resume an interrupted full run with unchanged solver sources:

```bash
python -m aocbb verify --resume --report reports/verification.json
```

The native solver can also accept your own uncompressed input for days 4, 5, 9, 11, 12, 15, and 17. It prints part 1 and part 2 on separate lines. Supported input domains are described in the algorithm notes.

```bash
./build/solver 15 data/15-1000.in
```

## Validation and interpretation

The 16 unit-test groups include randomized comparisons against independent brute-force or simpler reference algorithms. The complete large-input run checks every published case, not only examples or reduced-size substitutes. See [results](reports/RESULTS.md) for actual timings and peak process memory, and [environment details](reports/environment.json) for the CPU and resource limits.

For days **6 and 14**, the author publishes digit counts and leading/trailing digits, plus residues for day 14. The verifier checks every published fingerprint and independently recomputes modular results using transition-matrix exponentiation. All decimal digits are computed exactly and saved, but there is no external full-digit reference to compare them against.

For **`9-4096-2`**, the author reports multiple local minima within some connected basins. This repository counts each connected non-9 basin once and matches the author's primary answer, **4,971,158,490,375**. It does not use the alternative duplicate-basin count.

The largest day-15 test actually computes the shortest path over **2.5 billion cells**. It does not assume paths are monotone or substitute a smaller grid. Native cave counts use 128-bit arithmetic; huge fish, polymer, diagnostic, and bracket results use arbitrary precision.

## Continuous integration

Every push and pull request compiles the native solver and runs the independent tests. GitHub Actions also offers a manual **Run workflow → full_suite** option that downloads all datasets, runs the complete verification, and uploads the new reports and answer files as an artifact. The full suite is not automatically rerun on each push.

## Repository layout

```text
src/solver.cpp              C++ kernels for the large grids and combinatorial cases
aocbb/exact.py              GMP polynomial arithmetic and independent modular checks
aocbb/solvers.py            Python solvers and native-kernel interface
aocbb/__main__.py           Case runner, checker, and checkpointed report generation
cases.json                 All 27 cases, download locations, hashes, and references
scripts/download.py        Input downloader and decompressor
scripts/summarize.py        Human-readable results table
tests/test_solvers.py       Independent small-case verification
answers/                   All 49 complete decimal outputs
reports/                   Recorded tests, timings, memory, and answer fingerprints
docs/ALGORITHMS.md          Algorithms, correctness arguments, and supported domains
```

## Attribution

The underlying puzzles are by **Eric Wastl**, [Advent of Code](https://adventofcode.com/2021). The synthetic Big Inputs, altered dimensions/iteration counts, and published reference values are by **Tomasz Kramkowski**. His collection page carries a [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) notice. The catalogue paraphrases its metadata and records its numerical reference checks; the English algorithm explanations and implementations here are newly written.

Original Advent of Code puzzle statements and personalized puzzle inputs are not redistributed. The synthetic datasets are downloaded from their author's published links when requested.
