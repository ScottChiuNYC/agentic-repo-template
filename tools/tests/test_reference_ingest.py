from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
import unittest

from tools import reference_ingest


class ReferenceIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "ref").mkdir()
        self.pdf = self.root / "ref" / "paper.pdf"
        self.pdf.write_bytes(b"%PDF-test")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_request(self, *, start: int = 1, end: int = 2, expected: str | None = None) -> Path:
        directory = self.root / reference_ingest.REQUEST_DIR
        directory.mkdir(parents=True)
        sha = expected or reference_ingest.blob_sha(self.pdf)
        (directory / "request.toml").write_text(
            f'version = 1\nsource = "ref/paper.pdf"\nexpected_source_blob_sha = "{sha}"\nstart_page = {start}\nend_page = {end}\n',
            encoding="utf-8",
        )
        (directory / "READY").write_text("ready\n", encoding="utf-8")
        return directory

    def test_plan_binds_source_blob_and_page_range(self) -> None:
        self.make_request()
        result = self.root / "plan.json"
        reference_ingest.plan(self.root, 5, result)
        data = json.loads(result.read_text(encoding="utf-8"))
        self.assertEqual(data["source"], "ref/paper.pdf")
        self.assertEqual(data["start_page"], 1)
        self.assertEqual(data["end_page"], 2)
        self.assertIn("source-", data["output_dir"])

    def test_rejects_moved_source(self) -> None:
        self.make_request(expected="0" * 40)
        with self.assertRaisesRegex(reference_ingest.Rejected, "SOURCE_MOVED"):
            reference_ingest.plan(self.root, 2, self.root / "plan.json")

    def test_rejects_overlarge_page_range(self) -> None:
        self.make_request(start=1, end=101)
        with self.assertRaisesRegex(reference_ingest.Rejected, "PAGE_RANGE"):
            reference_ingest.plan(self.root, 101, self.root / "plan.json")

    def test_validates_complete_transcript(self) -> None:
        transcript = self.root / "transcript.md"
        text = "# Reference\n\n## PDF page 1\n\none\n\n## PDF page 2\n\ntwo\n"
        transcript.write_text(text, encoding="utf-8")
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({
            "start_page": 1,
            "end_page": 2,
            "transcript_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "coverage": {"expected_pages": [1, 2], "transcribed_pages": [1, 2]},
        }), encoding="utf-8")
        reference_ingest.validate(transcript, manifest)

    def test_rejects_missing_page_marker(self) -> None:
        transcript = self.root / "transcript.md"
        text = "## PDF page 1\n\none\n"
        transcript.write_text(text, encoding="utf-8")
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({
            "start_page": 1,
            "end_page": 2,
            "transcript_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "coverage": {"expected_pages": [1, 2], "transcribed_pages": [1, 2]},
        }), encoding="utf-8")
        with self.assertRaisesRegex(reference_ingest.Rejected, "COVERAGE"):
            reference_ingest.validate(transcript, manifest)


if __name__ == "__main__":
    unittest.main()
