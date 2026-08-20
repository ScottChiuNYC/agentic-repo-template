from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from tools import remote_safe_patch, safe_patch


class RemoteSafePatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "note.txt").write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "add", "note.txt"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "switch", "-c", "task"], cwd=self.root, check=True, capture_output=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_request(self, target: str = "note.txt", *, blob: str | None = None) -> None:
        directory = self.root / remote_safe_patch.REQUEST_DIR
        directory.mkdir(parents=True)
        actual = blob or remote_safe_patch.head_blob_sha(self.root, "note.txt")
        (directory / "request.toml").write_text(
            f'version = 1\ntarget = "{target}"\nexpected_target_blob_sha = "{actual}"\nmax_changed_lines = 10\n',
            encoding="utf-8",
        )
        (directory / "old.txt").write_text("old\n", encoding="utf-8")
        (directory / "new.txt").write_text("new\n", encoding="utf-8")
        (directory / "READY").write_text("ready\n", encoding="utf-8")

    def test_loads_valid_request(self) -> None:
        self.make_request()
        request, _ = remote_safe_patch.load_request(self.root)
        self.assertEqual(request.target, "note.txt")
        self.assertEqual(request.max_changed_lines, 10)

    def test_rejects_protected_workflow_target(self) -> None:
        self.make_request(".github/workflows/evil.yml")
        with self.assertRaisesRegex(safe_patch.SafePatchError, "PROTECTED_TARGET"):
            remote_safe_patch.load_request(self.root)

    def test_rejects_stale_target_blob(self) -> None:
        self.make_request(blob="0" * 40)
        request, _ = remote_safe_patch.load_request(self.root)
        self.assertNotEqual(remote_safe_patch.head_blob_sha(self.root, request.target), request.expected_target_blob_sha)

    def test_rejects_extra_request_file(self) -> None:
        self.make_request()
        (self.root / remote_safe_patch.REQUEST_DIR / "extra.txt").write_text("x", encoding="utf-8")
        with self.assertRaisesRegex(safe_patch.SafePatchError, "REQUEST_SHAPE"):
            remote_safe_patch.load_request(self.root)


if __name__ == "__main__":
    unittest.main()
