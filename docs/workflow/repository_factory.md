# Repository Factory

The template repository can act as a controlled repository factory so an authorized AI agent can create a new repository without access to a VPS or an interactive GitHub Settings session.

## Trust boundary

The factory is intentionally active only in `ScottChiuNYC/agentic-repo-template`.

- The workflow triggers only when a new issue is opened.
- The issue author must be the template repository owner.
- The issue title must begin with `repo-factory: `.
- The request body must be exactly `visibility=private` or `visibility=public`.
- Repository names are restricted to letters, numbers, `.`, `_`, and `-`.
- `REPO_FACTORY_TOKEN` exists only as an Actions secret in the template repository and is never copied by GitHub templates.
- Copies of `repo-factory.yml` in repositories created from this template are inert because the workflow checks the exact template repository name before running.
- Pull requests and arbitrary public issues cannot access the factory credential.

## Request protocol

Create an issue in the template repository with:

```text
Title: repo-factory: my-project
Body: visibility=private
```

For a public repository use:

```text
Body: visibility=public
```

The workflow passes the validated request to `bootstrap/new_repo.sh` with `--no-drive-secrets`. The bootstrap then creates the repository, applies the standard repository settings, and verifies the resulting state.

On success, the workflow comments on and closes the control issue. On failure, it leaves a failure comment and the workflow logs contain the non-secret diagnostic details.

## Credential

The template repository requires the Actions secret:

```text
REPO_FACTORY_TOKEN
```

The intended credential is a fine-grained personal access token for resource owner `ScottChiuNYC`, with access to all repositories and the minimum repository permissions needed by the current factory:

```text
Administration: Read and write
Contents: Read-only
Metadata: Read-only (GitHub-required)
```

Do not add Google Drive, Actions-secrets, or broader contents-write permissions unless the factory gains a documented feature that requires them.

Treat the token as a high-value credential: never place it in source, issue bodies, PRs, logs, chat, or VPS files. Rotate or revoke it immediately if exposure is suspected.

## Relationship to VPS bootstrap

`bootstrap/new_repo.sh` remains the implementation backend and the trusted-host/VPS fallback. The GitHub Actions factory is the preferred remote control plane when `REPO_FACTORY_TOKEN` is configured.

The current Actions factory deliberately uses `--no-drive-secrets`. Google Drive publication can be configured separately after repository creation if a project needs it.
