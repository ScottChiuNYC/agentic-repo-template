#!/usr/bin/env python3
"""Validate and apply one connector-authored remote Safe Patch request."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import safe_patch

REQUEST_DIR = Path(".github/safe-patch-request")
REQUEST_FILES = {"request.toml", "old.txt", "new.txt", "READY"}
HARD_MAX_CHANGED_LINES = 80
FORBIDDEN_PREFIXES = (
    ".github/workflows/",
    f"{REQUEST_DIR.as_posix()}/",
)
FORBIDDEN_TARGETS = {
    "tools/check_markdown_math.py",
    "tools/safe_patch.py",
    "tools/remote_safe_patch.py",
    "tools/remote_safe_patch_control.py",
}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


@dataclass(frozen=True)
class Request:
    target: str
    expected_target_blob_sha: str
    max_changed_lines: int


def reject(code: str, message: str) -> None:
    raise safe_patch.SafePatchError(code, message)


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        reject("REMOTE_SAFE_PATCH_REJECTED_NON_UTF8", f"request file must be UTF-8: {path}")
        raise AssertionError from exc


def validate_request_dir(root: Path) -> Path:
    raw = root / REQUEST_DIR
    if raw.is_symlink() or not raw.is_dir():
        reject("REMOTE_SAFE_PATCH_REJECTED_REQUEST_MISSING", REQUEST_DIR.as_posix())
    entries = list(raw.iterdir())
    if {p.name for p in entries} != REQUEST_FILES or any(p.is_symlink() or not p.is_file() for p in entries):
        reject("REMOTE_SAFE_PATCH_REJECTED_REQUEST_SHAPE", "request directory must contain exactly request.toml, old.txt, new.txt, READY")
    if read_utf8(raw / "READY").strip() != "ready":
        reject("REMOTE_SAFE_PATCH_REJECTED_NOT_READY", "READY must contain 'ready'")
    return raw


def load_request(root: Path) -> tuple[Request, Path]:
    directory = validate_request_dir(root)
    payload = tomllib.loads(read_utf8(directory / "request.toml"))
    required = {"version", "target", "expected_target_blob_sha", "max_changed_lines"}
    if set(payload) != required or payload.get("version") != 1:
        reject("REMOTE_SAFE_PATCH_REJECTED_REQUEST_FIELDS", "unexpected request fields/version")
    target = payload["target"]
    if not isinstance(target, str) or not target or target.startswith("/") or Path(target).as_posix() != target or ".." in Path(target).parts:
        reject("REMOTE_SAFE_PATCH_REJECTED_TARGET", "target must be a normalized repository-relative path")
    if target in FORBIDDEN_TARGETS or any(target.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        reject("REMOTE_SAFE_PATCH_REJECTED_PROTECTED_TARGET", target)
    expected = payload["expected_target_blob_sha"]
    if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
        reject("REMOTE_SAFE_PATCH_REJECTED_BLOB_SHA", "expected_target_blob_sha must be 40 hex characters")
    budget = payload["max_changed_lines"]
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= HARD_MAX_CHANGED_LINES:
        reject("REMOTE_SAFE_PATCH_REJECTED_LINE_BUDGET", f"budget must be 1..{HARD_MAX_CHANGED_LINES}")
    return Request(target, expected.lower(), budget), directory


def head_blob_sha(root: Path, target: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{target}"], text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        reject("REMOTE_SAFE_PATCH_REJECTED_TARGET_BLOB", completed.stderr.strip())
    return completed.stdout.strip().lower()


def write_result(path: Path | None, request: Request, changed_lines: int) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"target": request.target, "expected_target_blob_sha": request.expected_target_blob_sha, "changed_lines": changed_lines}, indent=2) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    safe_patch.ensure_safe_branch(root)
    safe_patch.ensure_expected_head(root, args.expected_head, required=True)
    request, directory = load_request(root)
    target = safe_patch.resolve_repo_file(root, request.target)
    safe_patch.ensure_clean_target(root, target)
    actual_blob = head_blob_sha(root, request.target)
    if actual_blob != request.expected_target_blob_sha:
        reject("REMOTE_SAFE_PATCH_REJECTED_TARGET_MOVED", f"expected {request.expected_target_blob_sha}, found {actual_blob}")
    plan = safe_patch.build_plan(root, target, read_utf8(directory / "old.txt"), read_utf8(directory / "new.txt"), maximum_changed_lines=request.max_changed_lines)
    sys.stdout.write(plan.diff)
    print(f"REMOTE_SAFE_PATCH_PREVIEW target={request.target} changed_lines={plan.changed_lines}")
    if args.write:
        safe_patch.apply_plan(root, plan, args.expected_head)
        print(f"REMOTE_SAFE_PATCH_APPLIED target={request.target} changed_lines={plan.changed_lines} head={args.expected_head}")
    write_result(args.result_json, request, plan.changed_lines)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--expected-head", required=True)
    p.add_argument("--result-json", type=Path)
    p.add_argument("--write", action="store_true")
    p.set_defaults(handler=run)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (safe_patch.SafePatchError, OSError, tomllib.TOMLDecodeError) as exc:
        code = getattr(exc, "code", "REMOTE_SAFE_PATCH_REJECTED_IO_ERROR")
        print(f"{code}: {exc}", file=sys.stderr)
        return getattr(exc, "exit_status", 3)


if __name__ == "__main__":
    raise SystemExit(main())
