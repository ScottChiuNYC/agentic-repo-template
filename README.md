# Agentic Repo Template

A reusable GitHub template for long-lived human-AI software collaboration.

The repository treats Git—not chat history—as durable project memory. It gives human developers and AI agents the same operating contracts, implementation specifications, mutation safeguards, validation gates, and publication path.

## What this template provides

- **Repository-backed memory**: `AGENTS.md`, `docs/START_HERE.md`, and `docs/CURRENT_STATE.md` establish the current source of truth.
- **Agent operating contracts**: explicit rules for research, implementation, GitHub mutation, documentation, and handoff.
- **Essence specifications**: a normative authoring and audit standard for implementation-ready human/AI contracts.
- **Fail-closed editing**: Safe Patch and Remote Safe Patch reject stale heads, ambiguous anchors, oversized diffs, protected targets, and invalid output.
- **Reference ingestion**: a source-versioned PDF transcription/OCR control plane for reusable research context.
- **Documentation validation**: Markdown/math checks run before publication.
- **Whole-repository publication**: CodeBinder converts the repository to a validated PDF artifact.
- **Optional Google Drive delivery**: Drive upload is enabled only when all four required repository secrets are configured; otherwise it is skipped cleanly.

## Architecture

```text
Human / AI agent
       |
       v
Repository contracts + durable state
       |
       +--> Essence specification
       |
       +--> Normal branch / PR workflow
       |
       +--> Safe Patch / Remote Safe Patch
       |
       v
Exact-head validation
       |
       v
Squash merge to main
       |
       v
CodeBinder PDF artifact
       |
       +--> GitHub Actions artifact
       |
       `--> Google Drive (optional)
```

## Start a new project

1. Create a repository from this template.
2. Replace the placeholders in `docs/CURRENT_STATE.md`.
3. Review `AGENTS.md` and customize project-specific rules only where necessary.
4. Apply the manual repository settings in `docs/workflow/repository_settings.md`.
5. If Google Drive publication is desired, configure the four documented Actions secrets.
6. Keep `main` authoritative; move stable conclusions from chat into the repository.

AI agents should begin with `AGENTS.md` and `docs/START_HERE.md`.

## Google Drive switch

The PDF workflow checks these repository secrets:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
```

Behavior is fail-closed:

- none present: build and retain the GitHub PDF artifact; skip Drive upload;
- all present: upload the PDF after a successful `main` build;
- only some present: fail the configuration check rather than silently publish incorrectly.

Secret values are never stored in this template and are not inherited by repositories created from a GitHub template.

## Design principles

- Repository state outranks stale conversation memory.
- Narrow changes should have narrow permissions and narrow diffs.
- Validation must apply to the exact commit that is merged.
- A frozen specification must not depend on hidden conversational context.
- Automation should fail closed when state, provenance, or intent is ambiguous.
- Project-specific domain assumptions do not belong in reusable infrastructure.

## Scope

This repository is development infrastructure, not an AI model framework, agent runtime, or domain-specific application skeleton. It intentionally excludes project-specific build systems, experiments, models, trading logic, and research content.
