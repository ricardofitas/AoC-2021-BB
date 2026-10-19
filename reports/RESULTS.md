# Full-size verification results

All **27 cases across 13 puzzle days** passed every published check.
The run produced **49 complete decimal answers**, stored in [`answers/`](../answers/).

For days 6 and 14, the reference only publishes fingerprints; those checks and
the independent modular checks passed. The complete decimal results are our computed
outputs, not full-digit comparisons with an external reference.

| Case | Result | Wall time (s) | Peak process RSS (MiB) | Answers |
|---|---|---:|---:|---|
| `3-1000001-100` | PASS | 1.245 | 344.4 | [part1](../answers/3-1000001-100-part1.txt) · [part2](../answers/3-1000001-100-part2.txt) |
| `4-3600-30` | PASS | 1.639 | 58.1 | [part1](../answers/4-3600-30-part1.txt) · [part2](../answers/4-3600-30-part2.txt) |
| `4-900-15` | PASS | 0.745 | 58.1 | [part1](../answers/4-900-15-part1.txt) · [part2](../answers/4-900-15-part2.txt) |
| `5-20000-6400` | PASS | 1.304 | 58.1 | [part1](../answers/5-20000-6400-part1.txt) · [part2](../answers/5-20000-6400-part2.txt) |
| `5-50000-10000` | PASS | 2.456 | 99.1 | [part1](../answers/5-50000-10000-part1.txt) · [part2](../answers/5-50000-10000-part2.txt) |
| `5-50000-10000000` | PASS | 14.839 | 1033.1 | [part1](../answers/5-50000-10000000-part1.txt) · [part2](../answers/5-50000-10000000-part2.txt) |
| `6-9999999` | PASS | 1.687 | 80.4 | [value](../answers/6-9999999-value.txt) |
| `6-67108864` | PASS | 4.832 | 166.0 | [value](../answers/6-67108864-value.txt) |
| `7-1000000-2` | PASS | 1.982 | 110.9 | [part1](../answers/7-1000000-2-part1.txt) · [part2](../answers/7-1000000-2-part2.txt) |
| `8-100000` | PASS | 2.724 | 78.5 | [part1](../answers/8-100000-part1.txt) · [part2](../answers/8-100000-part2.txt) |
| `9-4096-2` | PASS | 1.334 | 58.1 | [part1](../answers/9-4096-2-part1.txt) · [part2](../answers/9-4096-2-part2.txt) |
| `9-4096-4` | PASS | 1.139 | 58.1 | [part1](../answers/9-4096-4-part1.txt) · [part2](../answers/9-4096-4-part2.txt) |
| `10-10000-1000` | PASS | 1.120 | 58.1 | [part1](../answers/10-10000-1000-part1.txt) · [part2](../answers/10-10000-1000-part2.txt) |
| `10-10000-10000` | PASS | 7.740 | 58.8 | [part1](../answers/10-10000-10000-part1.txt) · [part2](../answers/10-10000-10000-part2.txt) |
| `11-100-2` | PASS | 0.714 | 58.1 | [part1](../answers/11-100-2-part1.txt) · [part2](../answers/11-100-2-part2.txt) |
| `11-1000-2` | PASS | 2.321 | 58.1 | [part1](../answers/11-1000-2-part1.txt) · [part2](../answers/11-1000-2-part2.txt) |
| `12-18-10-7-2` | PASS | 0.894 | 58.1 | [part1](../answers/12-18-10-7-2-part1.txt) · [part2](../answers/12-18-10-7-2-part2.txt) |
| `12-18-9-7` | PASS | 0.713 | 58.1 | [part1](../answers/12-18-9-7-part1.txt) · [part2](../answers/12-18-9-7-part2.txt) |
| `12-21-12-7` | PASS | 2.866 | 242.2 | [part1](../answers/12-21-12-7-part1.txt) · [part2](../answers/12-21-12-7-part2.txt) |
| `12-24-14-7` | PASS | 31.526 | 2086.8 | [part1](../answers/12-24-14-7-part1.txt) · [part2](../answers/12-24-14-7-part2.txt) |
| `14-100000` | PASS | 1.214 | 75.1 | [value](../answers/14-100000-value.txt) |
| `14-200000` | PASS | 1.667 | 92.0 | [value](../answers/14-200000-value.txt) |
| `14-1000000` | PASS | 5.289 | 189.5 | [value](../answers/14-1000000-value.txt) |
| `15-1000` | PASS | 3.565 | 58.1 | [part1](../answers/15-1000-part1.txt) · [part2](../answers/15-1000-part2.txt) |
| `15-10000` | PASS | 385.173 | 4867.5 | [part1](../answers/15-10000-part1.txt) · [part2](../answers/15-10000-part2.txt) |
| `17-117` | PASS | 0.659 | 58.1 | [part1](../answers/17-117-part1.txt) · [part2](../answers/17-117-part2.txt) |
| `17-50842` | PASS | 1.148 | 58.1 | [part1](../answers/17-50842-part1.txt) · [part2](../answers/17-50842-part2.txt) |

Sum of case wall times: **482.535 seconds**. Downloads, compilation, and the unit tests are excluded.
Each case runs in a fresh Python process; wall times include process startup, imports,
input reading, computation, verification, and writing answer files.
RSS is the maximum reported for the Python worker or its native child, not the sum
of concurrently resident processes. These are single-run observations on one machine,
not controlled cross-machine benchmarks.

- Platform: `Linux-6.18.55-x86_64-with-glibc2.39`
- Python: `3.12.14`; NumPy: `2.3.5`; gmpy2: `2.3.2`; SymPy: `1.14.0`
- Started: `2026-10-19T22:27:14.327702+00:00`
- Finished: `2026-10-19T22:35:16.915778+00:00`
- Solver source SHA-256: `306fb005972af60a183c15d02adf06b41f20817fa3c2f5f3d9d92f08ad5ee317`
- Compiler: GCC 13.3.0, `-O3 -DNDEBUG -std=c++20 -Wall -Wextra`.

The machine-readable [verification report](verification.json) includes complete small
answers, huge-number fingerprints, SHA-256 hashes of every answer file, individual
timings, and memory observations. [Algorithm notes](../docs/ALGORITHMS.md) explain the
methods, supported domains, and the broken-basin convention.
