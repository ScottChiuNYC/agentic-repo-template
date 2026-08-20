# CodeBinder PDF Pipeline

The publication workflow converts the whole repository into a reviewable PDF artifact.

## Trigger

`.github/workflows/publish-codebinder-pdf.yml` runs on:

- pull requests targeting `main`;
- pushes to `main`;
- manual dispatch.

PR runs build and validate the PDF but do not publish to Google Drive. `main` runs may publish externally when the optional Drive configuration is complete.

## Pipeline

```text
repository validation
-> install CodeBinder/Sphinx/LaTeX
-> whole-repository CodeBinder conversion
-> Sphinx LaTeX build
-> structural PDF validation
-> GitHub Actions artifact
-> optional Google Drive upload
```

The workflow rejects recursive ingestion of generated build output.

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
- **1-3/4 present**: workflow fails with a configuration error. Partial credential state is treated as misconfiguration, not as an implicit disable switch.

Repositories created from a GitHub template do not inherit secret values.

## Artifact naming

The local artifact uses a stable generic name. The Drive uploader derives the remote filename from the repository name, UTC timestamp, and short Git SHA unless `GOOGLE_DRIVE_FILE_NAME` overrides it.

## Validation

`tools/validate_pdf_build.py` checks that a PDF exists, is nontrivial, has an acceptable page count/table-of-contents structure, and that the LaTeX build log does not contain known fatal conditions.

XeLaTeX is the primary engine. The workflow can retry after disabling PDF bookmarks and can fall back to LuaLaTeX for robustness.

## Security

Only the upload step receives Google credentials. Credentials are never written to the repository or publication artifact.
