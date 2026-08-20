#!/usr/bin/env python3
"""Combine trusted-workflow page OCR text into Markdown plus a coverage manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

OCR_LANGUAGE = "eng"
OCR_PSM = 3
RENDER_DPI = 220
RENDER_MODE = "grayscale"


def fence(text: str) -> str:
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    return "`" * max(4, longest + 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--plan-json", required=True)
    parser.add_argument("--ocr-dir", required=True)
    parser.add_argument("--native-text", required=True)
    parser.add_argument("--tesseract-version", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    plan = json.loads(Path(args.plan_json).read_text(encoding="utf-8"))
    ocr_dir = Path(args.ocr_dir)
    start, end = plan["start_page"], plan["end_page"]
    native = Path(args.native_text).read_text(encoding="utf-8", errors="replace")
    native_chars = sum(c.isprintable() and not c.isspace() for c in native)
    pages = []

    lines = [
        f"# Reference transcript: {PurePosixPath(plan['source']).name}", "",
        "> Mechanical OCR transcript; no summarization or interpretation was performed.", ">",
        "> The source PDF remains authoritative for exact mathematics and visual content.", "",
        "## Provenance", "",
        f"- Source: `{plan['source']}`",
        f"- Source blob SHA: `{plan['source_blob_sha']}`",
        f"- PDF pages: {start}--{end}",
        f"- OCR engine: Tesseract `{args.tesseract_version}`",
        f"- OCR language: `{OCR_LANGUAGE}`",
        f"- Page segmentation mode: `{OCR_PSM}`",
        f"- Render resolution: {RENDER_DPI} DPI {RENDER_MODE}", "",
    ]
    for page in range(start, end + 1):
        path = ocr_dir / f"page-{page:04d}.txt"
        if not path.is_file():
            raise SystemExit(f"REFERENCE_INGEST_REJECTED_COVERAGE: page {page}")
        text = path.read_text(encoding="utf-8").replace("\x0c", "").rstrip()
        pages.append({"pdf_page": page, "characters": len(text), "empty": not bool(text), "ocr_sha256": hashlib.sha256(text.encode()).hexdigest()})
        lines += [f"## PDF page {page}", ""]
        if text:
            mark = fence(text)
            lines += [f"{mark}text", text, mark, ""]
        else:
            lines += ["**OCR returned no text. This page was not dropped; inspect the source PDF page visually.**", ""]

    transcript_text = "\n".join(lines).rstrip() + "\n"
    output = root / plan["output_dir"]
    output.mkdir(parents=True, exist_ok=False)
    transcript = output / "transcript.md"
    manifest = output / "manifest.json"
    transcript.write_text(transcript_text, encoding="utf-8")
    expected = list(range(start, end + 1))
    manifest.write_text(json.dumps({
        "schema_version": 1,
        "source_path": plan["source"],
        "source_blob_sha": plan["source_blob_sha"],
        "start_page": start,
        "end_page": end,
        "page_count": len(pages),
        "transcript_path": f"{plan['output_dir']}/transcript.md",
        "transcript_sha256": hashlib.sha256(transcript_text.encode()).hexdigest(),
        "native_text_layer_printable_characters": native_chars,
        "ocr": {"engine": "tesseract", "version": args.tesseract_version, "language": OCR_LANGUAGE, "page_segmentation_mode": OCR_PSM, "render_dpi": RENDER_DPI, "render_mode": RENDER_MODE},
        "coverage": {"expected_pages": expected, "transcribed_pages": expected, "empty_ocr_pages": [p["pdf_page"] for p in pages if p["empty"]]},
        "pages": pages,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFERENCE_INGEST_RENDERED {plan['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
