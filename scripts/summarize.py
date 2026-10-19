"""Create an English results table from the completed verification report."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / "reports/verification.json").read_text())
    manifest = json.loads((ROOT / "cases.json").read_text())
    expected_ids = {case["id"] for case in manifest["cases"]}
    cases = {case["id"]: case for case in report["cases"]}
    if set(cases) != expected_ids or not all(c["passed"] for c in cases.values()):
        raise SystemExit("A complete, successful verification report is required.")
    lines = [
        "# Full-size verification results",
        "",
        f"All **{len(cases)} cases across 13 puzzle days** passed every published check.",
        "The run produced **49 complete decimal answers**, stored in [`answers/`](../answers/).",
        "",
        "For days 6 and 14, the reference only publishes fingerprints; those checks and",
        "the independent modular checks passed. The complete decimal results are our computed",
        "outputs, not full-digit comparisons with an external reference.",
        "",
        "| Case | Result | Wall time (s) | Peak process RSS (MiB) | Answers |",
        "|---|---|---:|---:|---|",
    ]
    answer_count = 0
    for original in manifest["cases"]:
        case = cases[original["id"]]
        links = []
        for key, answer in case["answers"].items():
            path = ROOT / answer["file"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != answer["file_sha256"]:
                raise SystemExit(f"Answer checksum mismatch: {path}")
            links.append(f"[{key}](../{answer['file']})")
            answer_count += 1
        lines.append(
            f"| `{case['id']}` | PASS | {case['wall_seconds']:.3f} | {case['peak_process_rss_kib'] / 1024:.1f} | {' · '.join(links)} |"
        )
    assert answer_count == 49
    total = sum(c["wall_seconds"] for c in cases.values())
    lines += [
        "",
        f"Sum of case wall times: **{total:.3f} seconds**. Downloads, compilation, and the unit tests are excluded.",
        "Each case runs in a fresh Python process; wall times include process startup, imports,",
        "input reading, computation, verification, and writing answer files.",
        "RSS is the maximum reported for the Python worker or its native child, not the sum",
        "of concurrently resident processes. These are single-run observations on one machine,",
        "not controlled cross-machine benchmarks.",
        "",
        f"- Platform: `{report['platform']}`",
        f"- Python: `{report['python']}`; NumPy: `{report['numpy']}`; gmpy2: `{report['gmpy2']}`; SymPy: `{report['sympy']}`",
        f"- Started: `{report['started_at']}`",
        f"- Finished: `{report['finished_at']}`",
        f"- Solver source SHA-256: `{report['solver_source_sha256']}`",
        "- Compiler: GCC 13.3.0, `-O3 -DNDEBUG -std=c++20 -Wall -Wextra`.",
        "",
        "The machine-readable [verification report](verification.json) includes complete small",
        "answers, huge-number fingerprints, SHA-256 hashes of every answer file, individual",
        "timings, and memory observations. [Algorithm notes](../docs/ALGORITHMS.md) explain the",
        "methods, supported domains, and the broken-basin convention.",
        "",
    ]
    (ROOT / "reports/RESULTS.md").write_text("\n".join(lines))
    print(f"Published table for {len(cases)} cases and {answer_count} answer files.")


if __name__ == "__main__":
    main()
