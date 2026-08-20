# Remote Safe Patch

Remote Safe Patch exposes Safe Patch through a deliberately narrow GitHub control plane for environments where an agent can interact with GitHub but cannot safely hold unrestricted repository credentials.

## Request shape

The mutation workflow accepts a fixed request directory:

```text
.github/safe-patch-request/
├── request.toml
├── old.txt
├── new.txt
└── READY
```

`READY` must contain `ready`.

`request.toml` contains exactly:

```toml
version = 1
target = "path/to/tracked-file"
expected_target_blob_sha = "<40-hex git blob sha>"
max_changed_lines = 20
```

The workflow also binds the request to an exact PR head SHA.

## Fail-closed checks

The adapter rejects:

- malformed or extra request files;
- symlinked request files/directories;
- stale PR/head state;
- stale target blob SHA;
- path traversal or non-normalized paths;
- protected infrastructure targets;
- oversized changed-line budgets;
- ambiguous exact-text anchors;
- validation failures.

Remote Safe Patch cannot patch its own safety-critical workflow, validator, or core patch engine.

## Control issue

`remote-safe-patch-control.yml` maintains a durable GitHub issue that can be used as a connector-facing control surface. The control parser accepts a constrained command format and translates it into a normal PR-based Safe Patch transaction.

The permanent issue is control state, not project documentation. Do not place secrets in it.

## Trust boundary

The connector proposes intent. The GitHub workflow owns mutation authority and re-validates all safety conditions inside the repository checkout.

This separation prevents a remote agent from turning a narrow editing request into arbitrary repository write access.
