#!/usr/bin/env python3
"""Apply one narrow, fail-closed exact-text edit in a Git working tree."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import difflib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
from typing import Sequence

DEFAULT_MAX_CHANGED_LINES = 80
PROTECTED_BRANCHES = {"main", "master"}


class SafePatchError(RuntimeError):
    """A deterministic safe-patch rejection."""

    def __init__(self, code: str, message: str, exit_status: int = 3) -> None:
        super().__init__(message)
        self.code = code
        self.exit_status = exit_status


@dataclass(frozen=True)
class PatchPlan:
    path: Path
    original: str
    updated: str
    diff: str
    changed_lines: int


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise SafePatchError("SAFE_PATCH_REJECTED_GIT_ERROR", f"git {' '.join(args)} failed: {detail}")
    return completed


def discover_repo_root(start: Path | None = None) -> Path:
    base = (start or Path.cwd()).resolve()
    completed = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise SafePatchError("SAFE_PATCH_REJECTED_NOT_GIT_REPO", "safe_patch must run inside a Git working tree.")
    return Path(completed.stdout.strip()).resolve()


def current_head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def current_branch(root: Path) -> str:
    completed = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    branch = completed.stdout.strip()
    if completed.returncode != 0 or not branch:
        raise SafePatchError("SAFE_PATCH_REJECTED_DETACHED_HEAD", "safe_patch requires a named feature branch; detached HEAD is rejected.")
    return branch


def ensure_safe_branch(root: Path) -> str:
    branch = current_branch(root)
    if branch in PROTECTED_BRANCHES:
        raise SafePatchError("SAFE_PATCH_REJECTED_PROTECTED_BRANCH", f"refusing to patch protected branch {branch!r}; use a feature branch.")
    return branch


def ensure_expected_head(root: Path, expected_head: str | None, *, required: bool) -> str:
    actual = current_head(root)
    if required and not expected_head:
        raise SafePatchError("SAFE_PATCH_REJECTED_EXPECTED_HEAD_REQUIRED", "--expected-head is required with --write.")
    if expected_head and actual != expected_head:
        raise SafePatchError("SAFE_PATCH_REJECTED_HEAD_MOVED", f"HEAD moved: expected {expected_head}, found {actual}.")
    return actual


def resolve_repo_file(root: Path, raw_path: str | Path) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SafePatchError("SAFE_PATCH_REJECTED_PATH_ESCAPE", f"target path escapes repository root: {raw_path}") from exc
    if not resolved.is_file():
        raise SafePatchError("SAFE_PATCH_REJECTED_MISSING_TARGET", f"target must be an existing file: {resolved}")
    relative = resolved.relative_to(root).as_posix()
    tracked = _git(root, "ls-files", "--error-unmatch", "--", relative, check=False)
    if tracked.returncode != 0:
        raise SafePatchError("SAFE_PATCH_REJECTED_UNTRACKED_TARGET", f"target is not tracked by Git: {relative}")
    return resolved


def ensure_clean_target(root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    unstaged = _git(root, "diff", "--quiet", "--", relative, check=False)
    staged = _git(root, "diff", "--cached", "--quiet", "--", relative, check=False)
    if unstaged.returncode != 0 or staged.returncode != 0:
        raise SafePatchError("SAFE_PATCH_REJECTED_DIRTY_TARGET", f"target already has staged or unstaged changes: {relative}")


def _read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SafePatchError("SAFE_PATCH_REJECTED_NON_UTF8", f"safe_patch only edits UTF-8 text files: {path}") from exc


def _render_diff(root: Path, path: Path, old: str, new: str) -> str:
    relative = path.relative_to(root).as_posix()
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{relative}",
            tofile=f"b/{relative}",
        )
    )


def count_changed_lines(diff_text: str) -> int:
    changed = 0
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            in_hunk = True
        elif in_hunk and (line.startswith("+") or line.startswith("-")):
            changed += 1
    return changed


def build_plan(root: Path, path: Path, old_text: str, new_text: str, *, maximum_changed_lines: int) -> PatchPlan:
    if maximum_changed_lines < 1:
        raise SafePatchError("SAFE_PATCH_REJECTED_INVALID_BUDGET", "--max-changed-lines must be positive.")
    if not old_text:
        raise SafePatchError("SAFE_PATCH_REJECTED_EMPTY_ANCHOR", "exact replacement anchor must not be empty.")
    original = _read_utf8(path)
    matches = original.count(old_text)
    if matches == 0:
        raise SafePatchError("SAFE_PATCH_REJECTED_NO_MATCH", "exact replacement anchor was not found.")
    if matches != 1:
        raise SafePatchError("SAFE_PATCH_REJECTED_MULTIPLE_MATCHES", f"exact replacement anchor matched {matches} times; expected exactly one.")
    updated = original.replace(old_text, new_text, 1)
    if updated == original:
        raise SafePatchError("SAFE_PATCH_REJECTED_NO_CHANGE", "replacement would not change the target file.")
    diff = _render_diff(root, path, original, updated)
    changed_lines = count_changed_lines(diff)
    if changed_lines > maximum_changed_lines:
        raise SafePatchError("SAFE_PATCH_REJECTED_TOO_MANY_CHANGED_LINES", f"patch changes {changed_lines} lines; limit is {maximum_changed_lines}.")
    return PatchPlan(path, original, updated, diff, changed_lines)


def _validate_before_write(path: Path, updated: str) -> None:
    suffix = path.suffix.lower()
    try:
        if suffix == ".py":
            compile(updated, str(path), "exec")
        elif suffix == ".json":
            json.loads(updated)
        elif suffix == ".toml":
            tomllib.loads(updated)
    except (SyntaxError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        raise SafePatchError("SAFE_PATCH_REJECTED_VALIDATION_FAILED", f"syntax validation failed before write for {path}: {exc}", 6) from exc


def _write_atomic(path: Path, text: str) -> None:
    stat = path.stat()
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".safe_patch-", delete=False) as handle:
            temp_name = handle.name
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, stat.st_mode)
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def _validate_markdown(root: Path, path: Path) -> None:
    if path.suffix.lower() != ".md":
        return
    checker = root / "tools" / "check_markdown_math.py"
    if not checker.is_file():
        raise SafePatchError("SAFE_PATCH_REJECTED_VALIDATOR_MISSING", "Markdown target requires tools/check_markdown_math.py.", 6)
    relative = path.relative_to(root).as_posix()
    completed = subprocess.run(
        [sys.executable, str(checker), relative],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise SafePatchError("SAFE_PATCH_REJECTED_VALIDATION_FAILED", f"Markdown validation failed for {relative}:\n{completed.stdout.strip()}", 6)


def apply_plan(root: Path, plan: PatchPlan, expected_head: str) -> None:
    ensure_expected_head(root, expected_head, required=True)
    _validate_before_write(plan.path, plan.updated)
    _write_atomic(plan.path, plan.updated)
    try:
        ensure_expected_head(root, expected_head, required=True)
        relative = plan.path.relative_to(root).as_posix()
        changed = _git(root, "diff", "--name-only", "--", relative).stdout.splitlines()
        if changed != [relative]:
            raise SafePatchError("SAFE_PATCH_REJECTED_POST_WRITE_STATE", f"expected one changed target after write, found: {changed}")
        _validate_markdown(root, plan.path)
    except Exception:
        _write_atomic(plan.path, plan.original)
        raise


def run_doctor() -> int:
    root = discover_repo_root()
    try:
        branch = current_branch(root)
    except SafePatchError as exc:
        branch = f"<unavailable:{exc.code}>"
    checker = root / "tools" / "check_markdown_math.py"
    print(f"repo_root={root}")
    print(f"branch={branch}")
    print(f"head={current_head(root)}")
    print(f"protected_branch={branch in PROTECTED_BRANCHES}")
    print(f"markdown_checker={'present' if checker.is_file() else 'missing'}")
    return 0


def run_replace(args: argparse.Namespace) -> int:
    root = discover_repo_root()
    branch = ensure_safe_branch(root)
    ensure_expected_head(root, args.expected_head, required=args.write)
    path = resolve_repo_file(root, args.path)
    ensure_clean_target(root, path)
    plan = build_plan(root, path, _read_utf8(Path(args.old_file)), _read_utf8(Path(args.new_file)), maximum_changed_lines=args.max_changed_lines)
    sys.stdout.write(plan.diff)
    if plan.diff and not plan.diff.endswith("\n"):
        print()
    print(f"safe_patch preview: {plan.changed_lines} changed line(s).")
    if not args.write:
        print(f"DRY RUN on branch {branch!r}; no file was changed.")
        return 0
    apply_plan(root, plan, args.expected_head)
    relative = path.relative_to(root).as_posix()
    print(f"SAFE_PATCH_APPLIED {relative} changed_lines={plan.changed_lines} head={args.expected_head}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply one narrow exact-text edit to one existing tracked UTF-8 file. Dry run is the default; --write requires an exact HEAD guard.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor = subparsers.add_parser("doctor", help="Report repository/branch guards without changing files.")
    doctor.set_defaults(handler=lambda _: run_doctor())
    replace = subparsers.add_parser("replace", help="Replace one exact unique text anchor using snippet files.")
    replace.add_argument("--path", required=True)
    replace.add_argument("--old-file", required=True)
    replace.add_argument("--new-file", required=True)
    replace.add_argument("--expected-head")
    replace.add_argument("--max-changed-lines", type=int, default=DEFAULT_MAX_CHANGED_LINES)
    replace.add_argument("--write", action="store_true")
    replace.set_defaults(handler=run_replace)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except SafePatchError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_status
    except (OSError, UnicodeDecodeError) as exc:
        print(f"SAFE_PATCH_REJECTED_IO_ERROR: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
