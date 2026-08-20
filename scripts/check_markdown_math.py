#!/usr/bin/env python3
"""Fail on common Markdown/math delimiter mistakes."""

from __future__ import annotations

from pathlib import Path
import re
import sys

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_escaped(text: str) -> str:
    return re.sub(r"\\.", "", text)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    in_fence = False
    fence = ""
    display_open = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(raw)
        if match:
            marker = match.group(1)
            if not in_fence:
                in_fence, fence = True, marker
            elif marker == fence:
                in_fence, fence = False, ""
            continue
        if in_fence:
            continue

        line = INLINE_CODE_RE.sub("", raw)
        line = strip_escaped(line)
        display_count = line.count("$$")
        if display_count:
            if display_count > 2:
                errors.append(f"{path}:{lineno}: too many display-math delimiters on one line")
            if display_count % 2 == 1:
                display_open = not display_open
            line = line.replace("$$", "")

        if not display_open:
            singles = line.count("$")
            if singles % 2:
                errors.append(f"{path}:{lineno}: unmatched inline '$' delimiter")

    if in_fence:
        errors.append(f"{path}: unclosed fenced code block")
    if display_open:
        errors.append(f"{path}: unclosed '$$' display-math block")
    return errors


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv[1:]]
    if not paths:
        print("usage: check_markdown_math.py <file.md> [file.md ...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    for path in paths:
        if path.suffix.lower() == ".md":
            try:
                errors.extend(validate(path))
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{path}: {exc}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {len(paths)} Markdown file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
