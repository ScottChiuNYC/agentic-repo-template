# Writing and Markdown Rules

## Writing

- Prefer short, direct sentences.
- Keep technical density high; remove filler, not substance.
- Preserve equations, assumptions, algorithms, interfaces, edge cases, failure modes, and validation criteria.
- Distinguish normative requirements from examples and observations.
- Use stable terminology consistently.
- State uncertainty explicitly rather than smoothing it away.

## Markdown

- Use ATX headings (`#`, `##`, ...).
- Use fenced code blocks with a language tag when known.
- Keep one blank line around headings, lists, block quotes, and fenced blocks.
- Use standard Markdown links and relative repository paths where possible.
- Keep tables small; prefer bullets for long prose.
- Do not use raw HTML unless Markdown cannot express the requirement.

## Mathematics

- Inline math: `$...$`.
- Display math: use a standalone `$$...$$` block.
- Do not mix unmatched delimiters.
- Avoid putting display math inside Markdown tables.
- Preserve literal currency dollar signs by escaping them when they could be parsed as math.

`scripts/check_markdown_math.py` is the fail-closed repository validator for common delimiter and formatting errors.
