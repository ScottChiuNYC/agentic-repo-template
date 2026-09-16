from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_pdf_build.py"
SPEC = importlib.util.spec_from_file_location("validate_pdf_build", MODULE_PATH)
assert SPEC and SPEC.loader
validate_pdf_build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_pdf_build)


class ValidatePdfBuildTest(unittest.TestCase):
    def test_detects_nbsphinx_math_leakage_variants(self) -> None:
        bad_samples = (
            "alpha : nbsphinx-math : text{level}",
            "alpha nbsphinx -- math : text{level}",
            "alpha nbsphinx — math : text{level}",
        )
        for sample in bad_samples:
            self.assertTrue(
                any(
                    __import__("re").search(pattern, sample, __import__("re").IGNORECASE)
                    for pattern in validate_pdf_build.FORBIDDEN_PDF_TEXT_PATTERNS
                ),
                sample,
            )

    def test_allows_normal_math_text(self) -> None:
        sample = "alpha ↔ volatility level, rho ↔ skew"
        self.assertFalse(
            any(
                __import__("re").search(pattern, sample, __import__("re").IGNORECASE)
                for pattern in validate_pdf_build.FORBIDDEN_PDF_TEXT_PATTERNS
            )
        )


if __name__ == "__main__":
    unittest.main()
