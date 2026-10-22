---
name: codebinder-pdf
description: Use for repository-wide CodeBinder PDF generation, validation, GitHub Actions publication, optional Google Drive upload, and CodeBinder-specific Markdown/math rendering guardrails. Do not use for ordinary PDF/OCR tasks; use the routed external PDF skill instead.
compatibility: The publication path requires GitHub Actions. Local inspection can use the bundled Python scripts, but a full local PDF build additionally requires the CodeBinder/Sphinx/LaTeX toolchain.
---

# CodeBinder PDF

This skill owns the ART-provided repository PDF pipeline.

Use progressive disclosure:

- For publication behavior, GitHub Actions, artifacts, and Google Drive configuration, read `references/publication.md`.
- For Markdown math rules and the rendered-math regression guardrail, read `references/math-rendering.md`.
- Deterministic helpers live under `scripts/`.
- Regression tests for the helpers live under `tests/`.

The canonical GitHub workflow is:

`.github/workflows/publish-codebinder-pdf.yml`

## Boundary

This skill is for the repository-wide CodeBinder artifact. It does not replace a general PDF/OCR skill.

Do not add unrelated repository operating protocol here. Keep CodeBinder-specific behavior inside this skill and keep `AGENTS.md` as a router.
