# CodeBinder PDF Pipeline

## Purpose

The repository remains the complete source of truth. The CodeBinder PDF is a **human-facing project knowledge artifact**, not a byte-for-byte or file-for-file repository archive.

The default ART policy deliberately omits reusable agent/runtime infrastructure that is needed in Git but is not useful to reread in every child project's PDF.

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
-> project-focused Sphinx source tree
-> Sphinx / LaTeX build
-> structural PDF validation
-> GitHub Actions artifact
-> optional Google Drive upload
```

The workflow never executes project notebooks or application/research code merely to create the PDF.

## Default human-facing scope

Keep material that helps a reader understand the current project, including examples such as:

- `README.md`;
- `docs/CURRENT_STATE.md`;
- project architecture, research, specifications, derivations, and decisions;
- project implementation source and tests when supported by CodeBinder;
- project-specific learning material when a child repository intentionally re-includes it.

Omit machine-facing reusable ART infrastructure by default, including:

- `AGENTS.md`;
- `.github/`;
- `bootstrap/`;
- `tools/`;
- `docs/START_HERE.md`;
- generic writing/agent/audit/Safe Patch/reference-ingestion/repository-settings manuals under `docs/workflow/`;
- the CodeBinder pipeline manual itself;
- generated/transient output.

The canonical path list lives in root `.codebinderignore`.

A child repository MAY diverge when a nominally generic path becomes real project knowledge. In that case, change the child `.codebinderignore` explicitly and add a consumer assertion when useful. Do not weaken the template baseline silently.

## Validation

The conversion step proves both directions:

1. representative project-facing files are present in `build/codebinder-source`;
2. representative ART machine-facing paths are absent.

The generic template requires at least `README.md` and `docs/CURRENT_STATE.md`. Child repositories SHOULD replace or extend those smoke assertions with stable project-specific files.

`tools/validate_pdf_build.py` then validates the generated PDF, compiler log, page count, and TOC structure. A non-empty PDF alone is not sufficient evidence.

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

## Design rule

Treat these as separate products:

```text
Git repository
= project knowledge + implementation + AI operating system + CI/tooling

CodeBinder PDF
= project knowledge + reader-relevant implementation
```

An agent needing operating instructions reads them from Git. Their existence in Git does not imply that the owner should reread them in every generated project PDF.
