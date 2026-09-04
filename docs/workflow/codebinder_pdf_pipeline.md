# CodeBinder PDF Pipeline

## Purpose

The repository remains the complete source of truth. During the current **emerging workflow** stage, the CodeBinder PDF is a **review-complete human artifact**: it should expose tracked semantic and operational content that the owner may need to review, including material whose primary consumer is an AI agent.

The PDF is still not a byte-for-byte repository archive. Generated, transient, secret-bearing, raw-volume, or otherwise clearly non-reviewable content may remain excluded.

The governing rule is:

> **Do not exclude tracked content merely because it is AI-facing or machine-facing.**

## Trigger

`.github/workflows/publish-codebinder-pdf.yml` runs on:

- pull requests targeting `main`;
- pushes to `main`;
- manual dispatch.

PR runs build and validate the PDF but do not publish to Google Drive. `main` runs may publish externally when the optional Drive configuration is complete.

## Pipeline

```text
repository validation
-> CodeBinder discovery with .gitignore + .codebinderignore
-> review-complete Sphinx source tree
-> Sphinx / LaTeX build
-> structural PDF validation
-> GitHub Actions artifact
-> optional Google Drive upload
```

The workflow never executes project notebooks or application/research code merely to create the PDF.

## CJK text layout

The shared PDF workflow must support natural line breaking for Chinese/Japanese/Korean prose without requiring authors to insert manual spaces or hard line breaks into Markdown.

XeLaTeX builds therefore enable `xeCJK` and explicit Chinese line-breaking rules while retaining the Noto CJK font family. This is template-level publication infrastructure: child repositories should inherit the behavior rather than patching source prose to compensate for PDF overflow.

## Current review-complete scope

While ART and its consumer workflow are still evolving, keep tracked content that can materially affect repository behavior, authority, reviewability, or future implementation, including examples such as:

- `README.md` and `docs/CURRENT_STATE.md`;
- `AGENTS.md`;
- `.github/` workflow/configuration content;
- `bootstrap/` and `tools/`;
- `docs/START_HERE.md` and writing rules;
- generic agent, GitHub, durable-execution, audit, Safe Patch, reference-ingestion, repository-settings, and CodeBinder workflow manuals;
- project architecture, research, specifications, derivations, decisions, implementation source, and tests.

The current `.codebinderignore` should therefore be small and should normally contain only generated/transient/clearly non-reviewable material.

Representative exclusions may include:

- `build/` and `dist/`;
- `.git/`;
- temporary request/transport directories;
- raw transcripts when they are retained only as source material;
- caches such as `__pycache__/` and `*.pyc`;
- repository-specific large raw data that is clearly not useful as a human review surface.

A child repository MAY retain a repository-specific exclusion, but the reason should be review value or volume/transience—not the fact that an AI agent is the primary reader.

## Why this supersedes the earlier scope rule

The earlier policy treated CodeBinder primarily as a reader-facing project-knowledge PDF and intentionally omitted reusable ART operating infrastructure. That policy assumed the operating workflow was mature enough that the owner did not need to reread it routinely.

That assumption is premature while the workflow itself remains an active design object. AI-facing policy, authority chains, CI behavior, audit semantics, and durable-execution rules are part of the system being reviewed.

Therefore, during the emerging stage:

```text
AI-facing != human-irrelevant
machine-facing != non-reviewable
```

## Validation

The conversion step should prove both of these properties:

1. representative project/domain content is present;
2. representative workflow/operating content is also present.

At minimum, generic ART validation should confirm review visibility for stable representatives such as:

```text
README.md
AGENTS.md
docs/CURRENT_STATE.md
docs/workflow/AI_AGENT_OPERATING_POLICY.md
docs/workflow/INDEPENDENT_PRE_FREEZE_AUDIT.md
docs/workflow/DURABLE_EXECUTION_PROTOCOL.md
```

It should also verify that generated CodeBinder output is not recursively ingested.

Child repositories SHOULD extend these assertions with stable project-specific files and any repository-specific deliberate exclusion.

`tools/validate_pdf_build.py` then validates the generated PDF, compiler log, page count, and TOC structure. A non-empty PDF alone is not sufficient evidence.

## Future two-profile direction

Once the shared workflow is demonstrably stable, the preferred long-term design is not to rebuild a large machine-facing ignore list. Instead, CodeBinder may grow two explicit profiles:

```text
Review-complete PDF
= project/domain content + implementation + AI/workflow operating content

Reader-focused PDF
= project/domain content + reader-relevant implementation
```

Possible artifact names include `*-review.pdf` and `*-docs.pdf`.

This dual-profile design is a future direction only; the current implementation produces one review-complete PDF.

## Google Drive switch

Four repository secrets control Drive publication:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
```

Configuration states:

- **0/4 present**: Drive integration is disabled; PDF build/artifact still succeeds.
- **4/4 present**: Drive integration is enabled on successful `main` publication runs.
- **1-3/4 present**: workflow fails with a configuration error.

Repositories created from a GitHub template do not inherit secret values.

## Artifact naming

The local artifact uses a stable generic name. The Drive uploader derives the remote filename from repository name, UTC timestamp, and short Git SHA unless `GOOGLE_DRIVE_FILE_NAME` overrides it.

## Security

Only the upload step receives Google credentials. Credentials are never written to the repository or publication artifact.

Review-complete does not mean secret-complete: secrets, credential material, transient runtime state, and non-reviewable raw volume remain outside the PDF.

## Design rule

Current stage:

```text
Git repository
= complete tracked source of truth

CodeBinder PDF
= review-complete human surface over tracked semantic/operational content
```

The scope rule may later be split into explicit review-complete and reader-focused profiles, but should not silently hide AI-facing workflow while that workflow remains emerging.
