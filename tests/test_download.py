"""Check that cached inputs cannot silently change beneath a reproduced run."""

import hashlib
import lzma
import tempfile
import unittest
from pathlib import Path

from scripts.download import download


class DownloadIntegrityTests(unittest.TestCase):
    def test_download_cache_and_decompression_checksums(self):
        raw = b"010\n111\n"
        compressed = lzma.compress(raw)
        case = {
            "file": "synthetic.in.xz",
            "sha256": hashlib.sha256(compressed).hexdigest(),
            "input_sha256": hashlib.sha256(raw).hexdigest(),
        }
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / case["file"]).write_bytes(compressed)
            name, hashes = download(case, directory)
            self.assertEqual(name, case["file"])
            self.assertEqual(hashes["input_bytes"], len(raw))
            self.assertEqual((directory / "synthetic.in").read_bytes(), raw)
            (directory / "synthetic.in").write_bytes(b"changed\n")
            with self.assertRaisesRegex(ValueError, "Decompressed input checksum mismatch"):
                download(case, directory)

    def test_compressed_input_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / "synthetic.in.xz").write_bytes(lzma.compress(b"data"))
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                download({"file": "synthetic.in.xz", "sha256": "0" * 64}, directory)
