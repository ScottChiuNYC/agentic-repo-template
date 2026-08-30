# Agentic Repo Template (ART)

Agentic Repo Template (ART) is a reusable GitHub template for long-lived human-AI software collaboration.

ART treats Git—not chat history—as durable project memory. It gives human developers and AI agents the same operating contracts, implementation specifications, mutation safeguards, validation gates, and publication path.

## What ART provides

- **Repository-backed memory**: `AGENTS.md`, `docs/START_HERE.md`, and `docs/CURRENT_STATE.md` establish the current source of truth.
- **Agent operating contracts**: explicit rules for research, implementation, GitHub mutation, documentation, and handoff.
- **Essence specifications**: a normative authoring and audit standard for implementation-ready human/AI contracts.
- **Fail-closed editing**: Safe Patch and Remote Safe Patch reject stale heads, ambiguous anchors, oversized diffs, protected targets, and invalid output.
- **Reference ingestion**: a source-versioned PDF transcription/OCR control plane for reusable research context.
- **Documentation validation**: Markdown/math checks run before publication.
- **Project-focused publication**: CodeBinder builds a validated human-facing PDF from project knowledge and reader-relevant implementation while excluding reusable ART operating infrastructure.
- **Optional Google Drive delivery**: Drive upload is enabled only when all four required repository secrets are configured; otherwise it is skipped cleanly.
- **Automated repository bootstrap**: `bootstrap/new_repo.sh` creates a repository from ART, applies non-inherited GitHub settings, optionally installs Drive secrets from an external secret file, and verifies the resulting configuration.
- **Repository Factory control plane**: the ART repository can accept an owner-authored GitHub issue and run the bootstrap through GitHub Actions using a protected `REPO_FACTORY_TOKEN`.

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
Project-focused CodeBinder PDF artifact
       |
       +--> GitHub Actions artifact
       |
       `--> Google Drive (optional)
```

## Start a new project

### Repository Factory (preferred remote path)

When `REPO_FACTORY_TOKEN` is configured in `ScottChiuNYC/agentic-repo-template`, an authorized agent can create a control issue such as:

```text
Title: repo-factory: my-project
Body: visibility=private
```

The GitHub Actions workflow validates that the issue was authored by the ART repository owner, runs `bootstrap/new_repo.sh --no-drive-secrets`, verifies the new repository settings, and closes the control issue on success. The factory is hard-disabled in repositories copied from ART.

See `docs/workflow/repository_factory.md` for the request protocol and security boundary.

### Trusted-host / VPS bootstrap

On a trusted Linux host or VPS with GitHub CLI authenticated, run:

```bash
bash bootstrap/new_repo.sh my-project --private
```

The bootstrap utility:

1. creates the repository from ART;
2. enables automatic deletion of merged head branches;
3. ensures squash merge is available;
4. enables **Allow GitHub Actions to create and approve pull requests** while keeping the default `GITHUB_TOKEN` permission read-only;
5. installs the four Google Drive Actions secrets when the external secrets file is present;
6. reads the resulting GitHub state back and fails if verification does not match the intended configuration.

The default secret location is `~/.config/agentic-repo-bootstrap/google-drive.env`. Secret values are never stored in ART or sourced as shell code. See `docs/workflow/repository_settings.md` for one-time VPS setup, options, security rules, and the manual fallback.

After creation:

1. replace the placeholders in `docs/CURRENT_STATE.md`;
2. review `AGENTS.md` and customize project-specific rules only where necessary;
3. keep `main` authoritative and move stable conclusions from chat into the repository.

AI agents should begin with `AGENTS.md` and `docs/START_HERE.md`.

### Manual fallback

GitHub template repositories copy files but do not inherit repository settings or secret values. If the bootstrap utility is not used, manually configure:

1. **Allow GitHub Actions to create and approve pull requests**
   - `Settings` → `Actions` → `General` → `Workflow permissions`
   - enable **Allow GitHub Actions to create and approve pull requests**.
2. **Automatically delete head branches**
   - `Settings` → `General` → `Pull Requests`
   - enable **Automatically delete head branches**.
3. Add the optional Google Drive secrets under `Settings` → `Secrets and variables` → `Actions`.

Detailed instructions are in `docs/workflow/repository_settings.md`.

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

Secret values are never stored in ART and are not inherited by repositories created from a GitHub template. The bootstrap utility can copy them from a protected VPS-local dotenv file using `gh secret set`; GitHub CLI encrypts secret values before sending them to GitHub.

## Design principles

- Repository state outranks stale conversation memory.
- Narrow changes should have narrow permissions and narrow diffs.
- Validation must apply to the exact commit that is merged.
- A frozen specification must not depend on hidden conversational context.
- Automation should fail closed when state, provenance, or intent is ambiguous.
- Project-specific domain assumptions do not belong in reusable infrastructure.
- Credentials belong in external secret stores or GitHub Actions secrets, never in template files.
- Human-facing publication should omit reusable machine-facing infrastructure unless a child repository explicitly promotes it into project knowledge.

## Scope

ART is development infrastructure, not an AI model framework, agent runtime, or domain-specific application skeleton. It intentionally excludes project-specific build systems, experiments, models, trading logic, and research content.

## License

MIT. See `LICENSE`.
