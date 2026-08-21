# Repository Bootstrap and Settings

GitHub template repositories copy files, not repository settings or secret values. Prefer the VPS bootstrap utility for repeatable creation; use the manual procedure only as a fallback.

## Recommended: automated bootstrap

`bootstrap/new_repo.sh` creates a new repository from this template and applies the repository-level state that GitHub templates cannot inherit.

It performs these operations in order:

1. validates GitHub CLI authentication, the target repository name, and the configured template;
2. validates the external Google Drive secret file before any repository is created;
3. creates the repository from the template;
4. enables automatic deletion of merged head branches;
5. ensures squash merge is enabled;
6. enables **Allow GitHub Actions to create and approve pull requests** while keeping the default `GITHUB_TOKEN` permission read-only;
7. optionally installs the four Google Drive repository secrets;
8. reads repository settings and secret names back from GitHub and fails if verification does not match the requested state.

The script deliberately refuses to continue if the target repository already exists. A partial failure after repository creation is reported but never causes automatic repository deletion.

### VPS prerequisites

Install GitHub CLI (`gh`) on a trusted Linux host or VPS and authenticate once with an account or token that can:

- create repositories for the intended owner;
- administer repository settings;
- change repository Actions workflow permissions;
- write repository Actions secrets.

Verify authentication with:

```bash
gh auth status
```

The script does not store a GitHub token. GitHub CLI authentication remains responsible for credential storage.

### One-time Google Drive secret setup

If Google Drive publication is desired, create the secret file outside every Git repository:

```bash
mkdir -p ~/.config/agentic-repo-bootstrap
chmod 700 ~/.config/agentic-repo-bootstrap

cat > ~/.config/agentic-repo-bootstrap/google-drive.env <<'EOF'
GOOGLE_DRIVE_CLIENT_ID=<value>
GOOGLE_DRIVE_CLIENT_SECRET=<value>
GOOGLE_DRIVE_REFRESH_TOKEN=<value>
GOOGLE_DRIVE_FOLDER_ID=<value>
EOF

chmod 600 ~/.config/agentic-repo-bootstrap/google-drive.env
```

Do not commit this file, place it under a repository working tree, paste it into an issue/PR/chat, or keep screenshots of its contents.

The bootstrap script never executes the dotenv file as shell code. Before upload it rejects:

- symlinked secret files;
- group- or world-readable files on Linux;
- malformed entries;
- missing or duplicate required keys;
- keys outside the four-item allowlist;
- plainly empty values.

GitHub CLI performs the repository-secret upload. Secret values are encrypted locally before they are sent to GitHub.

### Create a repository

Private is the default:

```bash
bash bootstrap/new_repo.sh my-project
```

Explicit private/public examples:

```bash
bash bootstrap/new_repo.sh my-project --private
bash bootstrap/new_repo.sh public-demo --public
```

Useful options:

```text
--owner OWNER
--template OWNER/REPO
--secrets-file PATH
--no-drive-secrets
--require-drive-secrets
```

`--require-drive-secrets` is useful when Drive publication is mandatory: the script fails before repository creation if the external file is absent or invalid. Without that flag, a missing file is treated as an intentional Drive-disabled project.

Defaults can also be overridden with:

```text
AGENTIC_TEMPLATE_REPO
AGENTIC_BOOTSTRAP_SECRETS_FILE
```

For a short VPS command, install a wrapper or alias outside the repository, for example:

```bash
mkdir -p ~/bin
cat > ~/bin/newrepo <<'EOF'
#!/usr/bin/env bash
exec bash /path/to/agentic-repo-template/bootstrap/new_repo.sh "$@"
EOF
chmod 700 ~/bin/newrepo
```

Then repository creation becomes:

```bash
newrepo my-project
newrepo public-demo --public
```

## State applied by the bootstrap

### Allow GitHub Actions to create and approve pull requests

The script uses the repository Actions workflow-permissions API to enable the GitHub setting corresponding to:

**Settings -> Actions -> General -> Workflow permissions -> Allow GitHub Actions to create and approve pull requests**

It deliberately leaves the default `GITHUB_TOKEN` permission at `read`. Workflows that need write access must request the narrow scopes they need in their own `permissions:` block.

### Automatically delete merged branches

The script enables:

**Settings -> General -> Pull Requests -> Automatically delete head branches**

This keeps task branches disposable after squash merge.

### Squash merge

The script ensures squash merge is available because the repository workflow prefers focused PRs and squash merges. It does not disable other merge methods; projects may tighten merge policy separately when required.

### Google Drive repository secrets

When the external secret file is present and Drive installation is enabled, the script sets exactly:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
```

With no Drive secrets, publication skips Drive cleanly. A partial set intentionally fails the PDF workflow configuration check.

## Manual fallback

If the VPS bootstrap is unavailable, configure the same state manually after creating a repository from the template.

### 1. Allow GitHub Actions to create and approve pull requests

Repository **Settings -> Actions -> General -> Workflow permissions**:

- keep the default token permission as restrictive as practical;
- enable **Allow GitHub Actions to create and approve pull requests** when Remote Safe Patch/reference-ingestion control workflows are used.

Review workflow `permissions:` blocks independently.

### 2. Automatically delete merged branches

Repository **Settings -> General -> Pull Requests**:

- enable **Automatically delete head branches**.

### 3. Google Drive publication

Add all four under **Settings -> Secrets and variables -> Actions -> Repository secrets**.

Do not add placeholder or dummy values.

## Recommended security controls

- require two-factor authentication on the owning account;
- protect the VPS account and GitHub CLI credential store;
- keep the bootstrap secret file outside Git working trees and mode `0600`;
- keep workflow `GITHUB_TOKEN` permissions minimal;
- pin third-party Actions to trusted versions or commit SHAs for high-sensitivity projects;
- configure branch protection/rulesets when a project needs enforced review or required checks;
- never store production credentials in template files.
