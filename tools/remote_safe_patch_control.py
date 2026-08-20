#!/usr/bin/env python3
"""Prepare a trusted Remote Safe Patch request from a control issue body."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Sequence

LEGACY_CONTROL_MARKER = "[remote-safe-patch-request]"
INTENT_CONTROL_MARKER = "[remote-safe-patch-intent]"
REQUEST_DIR = Path(".github/safe-patch-request")
HARD_MAX_CHANGED_LINES = 80
MAX_SNIPPET_BYTES = 32768
FORBIDDEN_PREFIXES = (".github/workflows/", f"{REQUEST_DIR.as_posix()}/")
FORBIDDEN_TARGETS = {
    "scripts/check_markdown_math.py",
    "tools/safe_patch.py",
    "tools/remote_safe_patch.py",
    "tools/remote_safe_patch_control.py",
}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class ControlRequestError(ValueError):
    pass


@dataclass(frozen=True)
class ControlRequest:
    target: str
    expected_target_blob_sha: str
    max_changed_lines: int
    old: str
    new: str
    protocol_version: int = 1


def reject(code: str, detail: str = "") -> None:
    raise ControlRequestError(f"{code}: {detail}" if detail else code)


def validate_target(target: object) -> str:
    if not isinstance(target, str) or not target or any(ord(c) < 32 for c in target) or "\\" in target:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_TARGET")
    if target.startswith("/") or PurePosixPath(target).as_posix() != target or ".." in PurePosixPath(target).parts:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_TARGET")
    if target in FORBIDDEN_TARGETS or any(target.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_PROTECTED_TARGET")
    return target


def validate_budget(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= HARD_MAX_CHANGED_LINES:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_LINE_BUDGET")
    return value


def validate_snippets(old: object, new: object) -> tuple[str, str]:
    if not isinstance(old, str) or not old:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_OLD")
    if not isinstance(new, str):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_NEW")
    if len(old.encode()) > MAX_SNIPPET_BYTES or len(new.encode()) > MAX_SNIPPET_BYTES:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_SNIPPET_TOO_LARGE")
    return old, new


def git_blob_sha(root: Path, target: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{target}"], text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_TARGET_NOT_REGULAR_FILE", completed.stderr.strip())
    sha = completed.stdout.strip().lower()
    if not SHA_RE.fullmatch(sha):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_BLOB_SHA")
    return sha


def parse_literal(lines: list[str], start: int, key: str) -> tuple[str, int]:
    match = re.fullmatch(rf"{re.escape(key)}:\s*(\|-?)", lines[start])
    if not match:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_INTENT_SHAPE", lines[start])
    keep_newline = match.group(1) == "|"
    values: list[str] = []
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if re.fullmatch(r"(?:old|new):\s*\|-?", line):
            break
        if line and not line.startswith("  "):
            reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_INTENT_INDENT", line)
        values.append(line[2:] if line.startswith("  ") else "")
        index += 1
    text = "\n".join(values) + ("\n" if keep_newline else "")
    return text, index


def parse_intent(body: str, root: Path) -> ControlRequest:
    prefix = f"{INTENT_CONTROL_MARKER}\n"
    if not body.startswith(prefix) or "\r" in body:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_MARKER")
    lines = body[len(prefix):].split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) < 5 or lines[0] != "version: 2" or not lines[1].startswith("target: ") or not lines[2].startswith("max_changed_lines: "):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_INTENT_SHAPE")
    target = validate_target(lines[1][len("target: "):])
    raw_budget = lines[2][len("max_changed_lines: "):]
    if not raw_budget.isdigit():
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_LINE_BUDGET")
    budget = validate_budget(int(raw_budget))
    old, index = parse_literal(lines, 3, "old")
    if index >= len(lines):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_INTENT_SHAPE")
    new, index = parse_literal(lines, index, "new")
    if any(lines[index:]):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_INTENT_EXTRA")
    old, new = validate_snippets(old, new)
    return ControlRequest(target, git_blob_sha(root.resolve(), target), budget, old, new, 2)


def parse_legacy(body: str) -> ControlRequest:
    prefix = f"{LEGACY_CONTROL_MARKER}\n"
    if not body.startswith(prefix) or "\r" in body:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_MARKER")
    try:
        payload = json.loads(body[len(prefix):].strip())
    except json.JSONDecodeError as exc:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_JSON", str(exc))
    required = {"version", "target", "expected_target_blob_sha", "max_changed_lines", "old", "new"}
    if not isinstance(payload, dict) or set(payload) != required or payload["version"] != 1:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_FIELDS")
    target = validate_target(payload["target"])
    sha = payload["expected_target_blob_sha"]
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_BLOB_SHA")
    old, new = validate_snippets(payload["old"], payload["new"])
    return ControlRequest(target, sha.lower(), validate_budget(payload["max_changed_lines"]), old, new, 1)


def parse_control_body(body: str, root: Path | None = None) -> ControlRequest:
    if body.startswith(f"{INTENT_CONTROL_MARKER}\n"):
        if root is None:
            reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_REPO_ROOT_REQUIRED")
        return parse_intent(body, root)
    return parse_legacy(body)


def materialize_request(root: Path, request: ControlRequest) -> Path:
    directory = root.resolve() / REQUEST_DIR
    if directory.exists() or directory.is_symlink():
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_REQUEST_EXISTS")
    directory.mkdir(parents=True)
    (directory / "request.toml").write_text(
        "\n".join([
            "version = 1",
            f"target = {json.dumps(request.target, ensure_ascii=False)}",
            f'expected_target_blob_sha = "{request.expected_target_blob_sha}"',
            f"max_changed_lines = {request.max_changed_lines}",
            "",
        ]), encoding="utf-8")
    (directory / "old.txt").write_text(request.old, encoding="utf-8")
    (directory / "new.txt").write_text(request.new, encoding="utf-8")
    (directory / "READY").write_text("ready\n", encoding="utf-8")
    return directory


def run_prepare(args: argparse.Namespace) -> int:
    body = os.environ.get(args.body_env)
    if body is None:
        reject("REMOTE_SAFE_PATCH_CONTROL_REJECTED_BODY_ENV")
    root = Path(args.repo_root)
    request = parse_control_body(body, root)
    materialize_request(root, request)
    result = {k: v for k, v in asdict(request).items() if k not in {"old", "new"}}
    path = Path(args.result_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"REMOTE_SAFE_PATCH_CONTROL_PREPARED protocol=v{request.protocol_version} target={request.target} max_changed_lines={request.max_changed_lines}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--body-env", required=True)
    p.add_argument("--result-json", required=True)
    p.set_defaults(handler=run_prepare)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ControlRequestError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
