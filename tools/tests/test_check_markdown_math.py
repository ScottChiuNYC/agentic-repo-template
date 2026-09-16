from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_markdown_math.py"
SPEC = importlib.util.spec_from_file_location("check_markdown_math", MODULE_PATH)
assert SPEC and SPEC.loader
check_markdown_math = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_markdown_math)


class CheckMarkdownMathTest(unittest.TestCase):
    def validate_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.md"
            path.write_text(text, encoding="utf-8")
            return check_markdown_math.validate(path)

    def test_accepts_dollar_display_math(self) -> None:
        errors = self.validate_text("Before\n\n$$\n\\alpha \\leftrightarrow \\text{level}\n$$\n")
        self.assertEqual(errors, [])

    def test_rejects_backslash_display_math(self) -> None:
        errors = self.validate_text("Before\n\n\\[\n\\alpha \\leftrightarrow \\text{level}\n\\]\n")
        self.assertTrue(any("unsupported display-math delimiter" in error and r"\[" in error for error in errors))
        self.assertTrue(any("unsupported display-math delimiter" in error and r"\]" in error for error in errors))

    def test_ignores_delimiters_in_code(self) -> None:
        errors = self.validate_text("`\\[literal\\]`\n\n```text\n\\[literal\\]\n```\n")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
