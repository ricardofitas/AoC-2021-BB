#!/usr/bin/env python3
"""Download the author's synthetic inputs without adding them to Git."""

import argparse
import hashlib
import json
import lzma
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def download(case, directory):
    target = directory / case["file"]
    if not target.exists():
        temporary = target.with_name(target.name + ".partial")
        request = urllib.request.Request(
            case["url"], headers={"User-Agent": "AoC-2021-BB research solver"}
        )
        with (
            urllib.request.urlopen(request, timeout=120) as response,
            temporary.open("wb") as output,
        ):
            shutil.copyfileobj(response, output)
        temporary.replace(target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if case.get("sha256") and digest != case["sha256"]:
        raise ValueError(f"Checksum mismatch: {target.name}")
    unpacked = directory / target.name.removesuffix(".xz")
    if target.suffix == ".xz" and not unpacked.exists():
        temporary = unpacked.with_name(unpacked.name + ".partial")
        with lzma.open(target, "rb") as source, temporary.open("wb") as output:
            shutil.copyfileobj(source, output)
        temporary.replace(unpacked)
    with unpacked.open("rb") as stream:
        input_digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if case.get("input_sha256") and input_digest != case["input_sha256"]:
        raise ValueError(f"Decompressed input checksum mismatch: {unpacked.name}")
    print(f"Ready: {target.name}", flush=True)
    return target.name, {
        "sha256": digest,
        "input_sha256": input_digest,
        "input_bytes": unpacked.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--record-checksums", action="store_true")
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "cases.json"
    manifest = json.loads(manifest_path.read_text())
    unique = {c["file"]: c for c in manifest["cases"] if "file" in c}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        hashes = dict(pool.map(lambda c: download(c, args.data_dir), unique.values()))
    if args.record_checksums:
        for case in manifest["cases"]:
            if "file" in case:
                case.update(hashes[case["file"]])
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
