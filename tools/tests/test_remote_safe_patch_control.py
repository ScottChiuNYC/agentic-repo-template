from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from tools import remote_safe_patch_control as control


class RemoteSafePatchControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "note.txt").write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "add", "note.txt"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.root, check=True, capture_output=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_v2_intent_computes_blob_sha(self) -> None:
        body = "\n".join([
            "[remote-safe-patch-intent]",
            "version: 2",
            "target: note.txt",
            "max_changed_lines: 5",
            "old: |",
            "  old",
            "new: |",
            "  new",
            "",
        ])
        request = control.parse_control_body(body, self.root)
        self.assertEqual(request.target, "note.txt")
        self.assertEqual(request.expected_target_blob_sha, control.git_blob_sha(self.root, "note.txt"))
        self.assertEqual(request.old, "old\n")
        self.assertEqual(request.new, "new\n")

    def test_rejects_workflow_target(self) -> None:
        body = "\n".join([
            "[remote-safe-patch-intent]",
            "version: 2",
            "target: .github/workflows/evil.yml",
            "max_changed_lines: 5",
            "old: |-",
            "  x",
            "new: |-",
            "  y",
        ])
        with self.assertRaisesRegex(control.ControlRequestError, "PROTECTED_TARGET"):
            control.parse_control_body(body, self.root)

    def test_materializes_fixed_request_shape(self) -> None:
        request = control.ControlRequest("note.txt", control.git_blob_sha(self.root, "note.txt"), 5, "old\n", "new\n", 2)
        directory = control.materialize_request(self.root, request)
        self.assertEqual({p.name for p in directory.iterdir()}, {"request.toml", "old.txt", "new.txt", "READY"})
        self.assertEqual((directory / "READY").read_text(encoding="utf-8"), "ready\n")


if __name__ == "__main__":
    unittest.main()
