#!/usr/bin/env python3
"""Validate reference-ingestion requests and transcript page coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tomllib

REQUEST_DIR = Path(".github/reference-ingestion-request")
TRANSCRIPT_ROOT = Path("ref/transcripts")
MAX_PAGES = 100


class Rejected(RuntimeError):
    pass


def fail(code: str, detail: str = "") -> None:
    raise Rejected(f"{code}: {detail}" if detail else code)


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def source_path(value: object) -> str:
    if not isinstance(value, str) or not value or any(char in value for char in ("\x00", "\r", "\n")):
        fail("REFERENCE_INGEST_REJECTED_SOURCE")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or len(path.parts) < 2 or path.parts[0] != "ref" or path.suffix.lower() != ".pdf":
        fail("REFERENCE_INGEST_REJECTED_SOURCE", "expected a PDF below ref/")
    return path.as_posix()


def slug(source: str) -> str:
    path = PurePosixPath(source)
    relative = path.relative_to("ref").with_suffix("").as_posix()
    value = re.sub(r"[^a-z0-9]+", "-", relative.lower()).strip("-")
    return value or f"source-{hashlib.sha256(source.encode()).hexdigest()[:16]}"


def plan(root: Path, total_pages: int, result: Path) -> None:
    request_dir = root / REQUEST_DIR
    if request_dir.is_symlink() or not request_dir.is_dir():
        fail("REFERENCE_INGEST_REJECTED_REQUEST_MISSING")
    entries = list(request_dir.iterdir())
    if {item.name for item in entries} != {"request.toml", "READY"} or any(item.is_symlink() or not item.is_file() for item in entries):
        fail("REFERENCE_INGEST_REJECTED_REQUEST_SHAPE")
    if (request_dir / "READY").read_text(encoding="utf-8").strip() != "ready":
        fail("REFERENCE_INGEST_REJECTED_NOT_READY")
    data = tomllib.loads((request_dir / "request.toml").read_text(encoding="utf-8"))
    fields = {"version", "source", "expected_source_blob_sha", "start_page", "end_page"}
    if set(data) != fields or data["version"] != 1:
        fail("REFERENCE_INGEST_REJECTED_REQUEST_FIELDS")
    source = source_path(data["source"])
    expected = data["expected_source_blob_sha"]
    if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{40}", expected) is None:
        fail("REFERENCE_INGEST_REJECTED_BLOB_SHA")
    pdf = root / source
    if pdf.is_symlink() or not pdf.is_file() or blob_sha(pdf) != expected:
        fail("REFERENCE_INGEST_REJECTED_SOURCE_MOVED")
    start, end = data["start_page"], data["end_page"]
    if isinstance(start, bool) or not isinstance(start, int) or start < 1 or isinstance(end, bool) or not isinstance(end, int) or end < 0:
        fail("REFERENCE_INGEST_REJECTED_PAGE_RANGE")
    end = total_pages if end == 0 else end
    if end < start or end > total_pages or end - start + 1 > MAX_PAGES:
        fail("REFERENCE_INGEST_REJECTED_PAGE_RANGE")
    out = TRANSCRIPT_ROOT / slug(source) / f"source-{expected[:12]}" / f"pages-{start:04d}-{end:04d}"
    if (root / out).exists():
        fail("REFERENCE_INGEST_ALREADY_PRESENT", out.as_posix())
    payload = {"source": source, "source_blob_sha": expected, "start_page": start, "end_page": end, "page_count": end - start + 1, "output_dir": out.as_posix()}
    result.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


def validate(transcript: Path, manifest: Path) -> None:
    text = transcript.read_text(encoding="utf-8")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    expected = list(range(data["start_page"], data["end_page"] + 1))
    if data["coverage"]["expected_pages"] != expected or data["coverage"]["transcribed_pages"] != expected:
        fail("REFERENCE_INGEST_REJECTED_COVERAGE")
    for page in expected:
        if text.count(f"## PDF page {page}\n") != 1:
            fail("REFERENCE_INGEST_REJECTED_COVERAGE", str(page))
    if data["transcript_sha256"] != hashlib.sha256(text.encode()).hexdigest():
        fail("REFERENCE_INGEST_REJECTED_OUTPUT", "hash mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--total-pages", type=int, required=True)
    p.add_argument("--result-json", required=True)
    p = sub.add_parser("validate-output")
    p.add_argument("--transcript", required=True)
    p.add_argument("--manifest", required=True)
    args = parser.parse_args()
    try:
        if args.command == "plan":
            plan(Path(args.repo_root).resolve(), args.total_pages, Path(args.result_json).resolve())
        else:
            validate(Path(args.transcript).resolve(), Path(args.manifest).resolve())
    except (Rejected, OSError, ValueError, KeyError, TypeError, tomllib.TOMLDecodeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
