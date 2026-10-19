"""Run or verify the complete Big Inputs collection."""

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import gmpy2
import numpy
import sympy

from .solvers import ROOT, solve


def source_digest():
    digest = hashlib.sha256()
    for path in sorted([ROOT / "src/solver.cpp", *(ROOT / "aocbb").glob("*.py")]):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def fingerprint(value):
    number = gmpy2.mpz(value)
    result = {
        "digits": len(value),
        "prefix": value[:10],
        "suffix": value[-10:],
        "mod64": str(number % (2**64)),
        "mod32": str(number % (2**32)),
    }
    if len(value) <= 1000:
        result["exact"] = value
    return result


def check(value, expected):
    if isinstance(expected, str):
        return value == expected
    actual = fingerprint(value)
    return all(str(actual[key]) == str(item) for key, item in expected.items())


def worker(case, data_dir, answer_dir):
    values = solve(case, data_dir)
    answer_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, value in values.items():
        filename = f"{case['id']}-{key}.txt"
        payload = (value + "\n").encode("ascii")
        (answer_dir / filename).write_bytes(payload)
        results[key] = {
            **fingerprint(value),
            "file": f"answers/{filename}",
            "file_sha256": hashlib.sha256(payload).hexdigest(),
            "published_check_passed": check(value, case["expected"][key]),
            "published_check_type": "full_integer"
            if isinstance(case["expected"][key], str)
            else "fingerprint",
        }
    rss = max(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    )
    return {
        "id": case["id"],
        "day": case["day"],
        "passed": all(v["published_check_passed"] for v in results.values()),
        "answers": results,
        "peak_process_rss_kib": rss,
        "independent_moduli": ["1000003", "1000033", str(2**64)] if case["day"] in (6, 14) else [],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "run", "verify", "_worker"])
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Exact case ID; repeat to select multiple cases",
    )
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--answer-dir", type=Path, default=ROOT / "answers")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/verification.json")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse passed records only when solver source hashes match",
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / "cases.json").read_text())
    cases = manifest["cases"]
    if args.case_ids:
        missing = set(args.case_ids) - {c["id"] for c in cases}
        if missing:
            parser.error("Unknown case IDs: " + ", ".join(sorted(missing)))
        cases = [c for c in cases if c["id"] in args.case_ids]
    if args.command == "list":
        for case in cases:
            print(f"{case['id']:24s} day {case['day']:2d}")
        return
    if args.command == "_worker":
        if len(cases) != 1:
            parser.error("_worker requires one case")
        print(json.dumps(worker(cases[0], args.data_dir, args.answer_dir)))
        return
    revision = source_digest()
    report = {
        "source": manifest["source"],
        "started_at": datetime.now(UTC).isoformat(),
        "solver_source_sha256": revision,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "gmpy2": gmpy2.version(),
        "sympy": sympy.__version__,
        "rss_definition": "Maximum process RSS observed for the worker or its native child; KiB on Linux.",
        "cases": [],
    }
    if args.resume and args.report.exists():
        previous = json.loads(args.report.read_text())
        if previous.get("solver_source_sha256") != revision:
            parser.error("Cannot resume: solver sources have changed")
        report = previous
    finished = {c["id"] for c in report["cases"] if c.get("passed")}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        if case["id"] in finished:
            print(f"Already verified: {case['id']}", flush=True)
            continue
        print(f"Running {case['id']}...", flush=True)
        command = [
            sys.executable,
            "-m",
            "aocbb",
            "_worker",
            "--case",
            case["id"],
            "--data-dir",
            str(args.data_dir.resolve()),
            "--answer-dir",
            str(args.answer_dir.resolve()),
        ]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, check=False)
        seconds = time.perf_counter() - start
        if result.returncode:
            record = {
                "id": case["id"],
                "day": case["day"],
                "passed": False,
                "error": f"Worker exited with status {result.returncode}",
            }
        else:
            record = json.loads(result.stdout)
        record["wall_seconds"] = round(seconds, 3)
        report["cases"] = [c for c in report["cases"] if c["id"] != case["id"]] + [record]
        report["finished_at"] = datetime.now(UTC).isoformat()
        report["passed_cases"] = sum(c["passed"] for c in report["cases"])
        report["recorded_cases"] = len(report["cases"])
        temporary = args.report.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(args.report)
        print(
            f"{'PASS' if record['passed'] else 'FAIL'} {case['id']} ({seconds:.3f} s)", flush=True
        )
        if not record["passed"]:
            raise SystemExit(1)
    print(f"Verified {len(cases)} selected cases. Report: {args.report}")


if __name__ == "__main__":
    main()
