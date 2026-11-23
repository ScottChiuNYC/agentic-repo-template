# Repository setup

Copier generates files; it does not configure GitHub repository settings or copy secrets.
Complete this checklist when creating or adopting a repository, then read the settings back to verify them.

## GitHub settings

- Use `main` as the default branch. The generated PDF workflow targets `main`.
- Under **Settings → General → Pull Requests**, enable **Allow squash merging** and **Automatically delete head branches**. Verify deletion after the first merged PR; do not delete unrelated task branches.
- Under **Settings → Actions → General → Workflow permissions**, keep the default `GITHUB_TOKEN` permissions read-only. The PDF workflow requests only `contents: read`.
- Enable **Allow GitHub Actions to create and approve pull requests** only when a workflow actually creates or approves PRs using `GITHUB_TOKEN`. The generated PDF workflow does not need this setting, and it does not control PRs created through a separate GitHub connector or CLI authorization.
- If repository or organization policies prevent Actions or the pinned public GHCR builder image from running, resolve the specific restriction before treating PDF publication as ready.

## Local generated files

ART's PDF workflow creates `build/` and `dist/`; helper tests can create Python caches.
ART seeds `.gitignore` for a new repository, but Copier preserves an existing `.gitignore` so that another template or the project can own its rules.

For an existing repository, check `git check-ignore build/probe dist/probe .agents/skills/codebinder-pdf/scripts/__pycache__/probe.pyc` and add any missing rules without replacing unrelated ignores. Also preserve any independent language-template answers files. Git ignore rules do not remove files that are already tracked; review such files separately.

## Optional Google Drive publication

Under **Settings → Secrets and variables → Actions → Repository secrets**, configure all four together:

- `GOOGLE_DRIVE_CLIENT_ID`
- `GOOGLE_DRIVE_CLIENT_SECRET`
- `GOOGLE_DRIVE_REFRESH_TOKEN`
- `GOOGLE_DRIVE_FOLDER_ID`

Secret values are not inherited through either GitHub templates or Copier. Keep them out of repository files, PRs, logs, and PDF artifacts.

With no secrets, PDF builds retain their GitHub artifact and skip Drive. All four enable publication from successful `main` runs; a partial set fails the configuration check. PR runs never upload to Drive.

## First-use setup and every-merge verification

1. At first use, build a PDF on a PR and inspect the artifact for expected project content.
2. **After every merge**, verify the resulting `main` content, the completed PDF workflow and artifact for that exact merge SHA, and source-branch cleanup.
3. When Drive is configured, confirm that the Google Drive upload step ran successfully for that same `main` run **and independently read back the uploaded Drive file metadata** (file ID, name/SHA, size and destination) before reporting the task complete. A successful PR PDF check, build, or skipped upload is not enough.
4. When Drive is intentionally not configured, confirm the explicit skip and report that the PDF artifact exists but Google Drive publication is disabled. If required evidence is still pending or inaccessible, report the work as pending/unverified rather than complete.

Each project owns its content-completeness assertions. A structurally valid PDF can still omit a note; add representative-file checks to the project's publication workflow when needed rather than hard-coding domain filenames in ART.
