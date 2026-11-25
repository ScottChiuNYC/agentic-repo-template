"""Render Mermaid fences to PNG only in CodeBinder's disposable staging tree.

Tracked Markdown remains unchanged, so GitHub renders the original Mermaid;
CodeBinder/nbsphinx/LaTeX see the corresponding PNG image references.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Callable


FENCE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<info>[^\r\n]*)$")
PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")


def _closing(line: str, marker: str) -> bool:
    stripped = line.lstrip(" ")
    rest = stripped.rstrip(" \t")
    return (
        len(line) - len(stripped) <= 3
        and len(rest) >= len(marker)
        and rest == marker[0] * len(rest)
    )


def _check_png(path: Path) -> None:
    if not path.is_file() or path.stat().st_size <= len(PNG_SIGNATURE):
        raise RuntimeError(f"Mermaid did not produce a nonempty PNG: {path}")
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise RuntimeError(f"Mermaid produced a non-PNG image: {path}")


def cli_renderer(source: str, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=".mermaid-", dir=output.parent) as temp:
        input_path = Path(temp) / "diagram.mmd"
        input_path.write_text(source, encoding="utf-8")
        subprocess.run(
            [
                "mmdc",
                "-p",
                "/etc/mermaid-puppeteer.json",
                "-i",
                str(input_path),
                "-o",
                str(output),
                "-b",
                "white",
                "-w",
                "1400",
                "-s",
                "2",
            ],
            check=True,
        )


def render_markdown(
    path: Path, render: Callable[[str, Path], None] = cli_renderer
) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    result: list[str] = []
    index = 0
    i = 0
    while i < len(lines):
        opening = FENCE.fullmatch(lines[i].rstrip("\r\n"))
        if opening is None:
            result.append(lines[i])
            i += 1
            continue

        marker = opening.group("marker")
        info = opening.group("info").strip()
        end = i + 1
        while end < len(lines) and not _closing(lines[end].rstrip("\r\n"), marker):
            end += 1
        if end >= len(lines):
            if info == "mermaid":
                raise ValueError(f"Unclosed Mermaid fence in {path} at line {i+1}")
            result.extend(lines[i:])
            break

        if info == "mermaid":
            source = "".join(lines[i + 1:end]).strip()
            if not source:
                raise ValueError(f"Empty Mermaid fence in {path} at line {i+1}")
            index += 1
            # ASCII filename avoids broken Markdown links for names with spaces.
            file_key = hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:12]
            filename = f"mermaid-{file_key}-{index:03d}.png"
            output = path.with_name(filename)
            if output.exists():
                raise FileExistsError(f"Mermaid output already exists: {output}")
            render(source + "\n", output)
            _check_png(output)
            result.append(f"![Mermaid diagram {index}]({filename})\n")
        else:
            # Do not turn nested example Mermaid snippets into diagrams.
            result.extend(lines[i:end + 1])
        i = end + 1

    if index:
        path.write_text("".join(result), encoding="utf-8")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Disposable CodeBinder staging directory")
    args = parser.parse_args()
    root = args.root
    if not root.is_dir():
        parser.error(f"Not a directory: {root}")
    total = sum(render_markdown(path) for path in sorted(root.rglob("*.md")))
    print(f"Rendered {total} Mermaid diagrams for PDF staging.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
