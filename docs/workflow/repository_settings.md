# Repository Settings

GitHub template repositories copy files, not repository settings or secret values. Apply these settings after creating a new repository.

## Required manual settings

### 1. Allow GitHub Actions to create pull requests

Repository **Settings -> Actions -> General -> Workflow permissions**:

- select the least privilege appropriate to the project;
- enable **Allow GitHub Actions to create and approve pull requests** when Remote Safe Patch/reference-ingestion control workflows are used.

Review workflow `permissions:` blocks independently; repository-level permission is only the outer ceiling.

### 2. Automatically delete merged branches

Repository **Settings -> General -> Pull Requests**:

- enable **Automatically delete head branches**.

This keeps task branches disposable after squash merge.

## Optional Google Drive publication

Add all four under **Settings -> Secrets and variables -> Actions -> Repository secrets**:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
```

Do not add placeholder or dummy values. With no Drive secrets, publication skips Drive cleanly. A partial set intentionally fails the configuration check.

## Recommended

- require two-factor authentication on the owning account;
- keep workflow `GITHUB_TOKEN` permissions minimal;
- pin third-party Actions to trusted versions or commit SHAs for high-sensitivity projects;
- configure branch protection/rulesets when the project needs enforced review or required checks;
- never store production credentials in template files.
