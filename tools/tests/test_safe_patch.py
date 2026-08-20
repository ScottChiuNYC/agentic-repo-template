from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from tools import safe_patch


class SafePatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "sample.py").write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "sample.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "switch", "-c", "task"], cwd=self.root, check=True, capture_output=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_rejects_protected_branch(self) -> None:
        subprocess.run(["git", "switch", "main"], cwd=self.root, check=True, capture_output=True)
        with self.assertRaisesRegex(safe_patch.SafePatchError, "protected branch"):
            safe_patch.ensure_safe_branch(self.root)

    def test_rejects_stale_head(self) -> None:
        with self.assertRaisesRegex(safe_patch.SafePatchError, "HEAD moved"):
            safe_patch.ensure_expected_head(self.root, "0" * 40, required=True)

    def test_requires_unique_anchor(self) -> None:
        path = self.root / "sample.py"
        path.write_text("value = 1\nvalue = 1\n", encoding="utf-8")
        with self.assertRaisesRegex(safe_patch.SafePatchError, "matched 2 times"):
            safe_patch.build_plan(self.root, path, "value = 1", "value = 2", maximum_changed_lines=10)

    def test_apply_exact_patch(self) -> None:
        path = self.root / "sample.py"
        head = safe_patch.current_head(self.root)
        plan = safe_patch.build_plan(self.root, path, "value = 1", "value = 2", maximum_changed_lines=10)
        safe_patch.apply_plan(self.root, plan, head)
        self.assertEqual(path.read_text(encoding="utf-8"), "value = 2\n")

    def test_rejects_invalid_python_before_write(self) -> None:
        path = self.root / "sample.py"
        head = safe_patch.current_head(self.root)
        plan = safe_patch.build_plan(self.root, path, "value = 1", "if:\n", maximum_changed_lines=10)
        with self.assertRaisesRegex(safe_patch.SafePatchError, "syntax validation"):
            safe_patch.apply_plan(self.root, plan, head)
        self.assertEqual(path.read_text(encoding="utf-8"), "value = 1\n")


if __name__ == "__main__":
    unittest.main()
