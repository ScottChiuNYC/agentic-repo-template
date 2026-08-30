# Remote Safe Patch

## Purpose

Remote Safe Patch exposes the repository's fail-closed Safe Patch engine through a narrow GitHub control plane for connector-only environments.

The preferred route lets an authenticated owner express one exact narrow edit by updating a permanent control issue. Trusted GitHub Actions then constructs the engine request, creates an isolated task branch, applies deterministic guards, pushes the exact target change, and opens a result PR.

Use this path only for a narrow exact edit to one existing tracked UTF-8 file. New files, multi-file changes, renames, deletions, intentional whole-document rewrites, and changes to the patch infrastructure itself use the normal feature-branch/PR workflow.

## 1. Architecture

The layers are:

```text
connector / owner intent
-> permanent [remote-safe-patch-control] issue
-> .github/workflows/remote-safe-patch-control.yml
-> tools/remote_safe_patch_control.py
-> tools/remote_safe_patch.py
-> tools/safe_patch.py
-> isolated result branch / PR
```

The connector proposes exact edit intent. Trusted repository code owns request construction, current-state binding, validation, mutation, branch creation, and PR creation.

The legacy PR-comment executor `.github/workflows/remote-safe-patch.yml` remains a recovery route when the permanent control issue cannot be used.

## 2. Preferred v2 control request

The permanent issue title is exactly:

```text
[remote-safe-patch-control]
```

The preferred request body uses the v2 literal-block protocol:

```text
[remote-safe-patch-intent]
version: 2
target: docs/example.md
max_changed_lines: 6
old: |
  The old sentence with \alpha.
new: |
  The revised sentence with \beta.
```

V2 deliberately keeps the connector-facing request low-entropy:

- `old` and `new` are literal text blocks rather than JSON-escaped strings;
- the connector does not provide the target blob SHA;
- trusted code computes the target blob SHA from the exact checked-out repository state before constructing the internal engine request.

The request is still exact-edit intent, not free-form natural language. `old` must match exactly and uniquely.

## 3. V2 request constraints

The control parser fails closed unless all applicable constraints hold:

- the marker and `version: 2` shape are exact;
- `target` is a normalized repository-relative POSIX path;
- the target is not protected patch/workflow infrastructure;
- `max_changed_lines` is an integer from 1 through 80;
- `old` is non-empty;
- both snippets fit the repository byte limit;
- literal-block indentation and trailing-newline semantics are valid;
- the target exists at the checked-out repository state and has a valid Git blob identity.

`|` preserves a final newline; `|-` omits it.

If the exact old anchor is stale or non-unique, the deterministic executor rejects the request rather than guessing the intended paragraph.

## 4. Stable v1 rollback protocol

The permanent control issue also accepts the older JSON protocol:

```text
[remote-safe-patch-request]
{"version":1,"target":"docs/example.md","expected_target_blob_sha":"0123456789abcdef0123456789abcdef01234567","max_changed_lines":6,"old":"The old sentence.\n","new":"The revised sentence.\n"}
```

The v1 object contains exactly:

```text
version
target
expected_target_blob_sha
max_changed_lines
old
new
```

V1 remains a rollback path for the connector-facing preparation contract. Both v1 and v2 ultimately materialize the same trusted internal Safe Patch request shape before mutation.

## 5. Trusted transaction

For an accepted permanent-issue request, the workflow:

1. checks out trusted default-branch state;
2. creates a unique isolated transaction branch;
3. parses and validates the issue body with `tools/remote_safe_patch_control.py`;
4. for v2, computes the target blob SHA from checked-out `HEAD`;
5. materializes `.github/safe-patch-request/` only inside the runner;
6. applies `tools/remote_safe_patch.py` and the core `tools/safe_patch.py` engine;
7. removes the runner-local request directory;
8. requires the working-tree diff to contain exactly the requested target;
9. commits and pushes without force;
10. opens a focused result PR;
11. comments the result on the control issue;
12. restores the permanent issue to `Status: ready.`.

The generated PR contains the substantive target edit, not the temporary request directory.

## 6. Safety contract

Remote Safe Patch preserves the core Safe Patch guarantees. Applicable guards include:

- one existing tracked UTF-8 target;
- protected-branch / protected-target rejection;
- exact expected local `HEAD` where mutation occurs;
- exact target blob binding;
- one exact unique old-text match;
- no-op rejection;
- changed-line budget enforcement;
- supported Python, JSON, TOML, and Markdown validation;
- target-only post-write diff;
- clean post-commit work tree;
- no force push.

Remote requests cannot patch the Safe Patch workflows, request directory, core patch engines, control parser, or other explicitly protected infrastructure.

## 7. Result PR validation

A generated PR is not merge authority by itself.

The agent MUST return to the ordinary repository workflow:

```text
READ generated PR and exact head SHA
-> READ target from that exact head
-> VERIFY target-only semantic diff
-> VERIFY mergeability and required checks on exact head
-> SQUASH MERGE exact validated head
-> VERIFY main
-> VERIFY applicable publication/artifacts
-> VERIFY branch cleanup
```

If GitHub does not automatically start ordinary PR workflows for a PR created by `GITHUB_TOKEN`, recover the existing PR using the repository's documented GitHub workflow rather than creating a duplicate mutation transaction.

Repository/Actions state is authoritative; issue comments are convenience status only.

## 8. Failure and recovery

A rejected guard does not authorize blind retry.

Use:

```text
rejection / timeout / unknown result
-> re-read control issue
-> inspect Actions run/job
-> search for any surviving result branch or PR
-> re-read current target/main state
-> determine which invariant actually holds
-> repair or recover only what is missing
```

For a stale exact anchor, re-fetch the current target and rebuild the request. For an oversized or non-narrow change, stop using Remote Safe Patch and switch to the ordinary branch/PR route.

If the target commit/branch already exists but PR creation failed, recover that transaction rather than replaying the patch.

## 9. Repository setting

The happy path expects:

**Settings -> Actions -> General -> Workflow permissions -> Allow GitHub Actions to create and approve pull requests**

The repository bootstrap procedure configures this setting while retaining restrictive default `GITHUB_TOKEN` permissions. Workflows request only the write scopes needed for their own jobs.

See [`repository_settings.md`](repository_settings.md).

## 10. Supported routes

```text
local Git checkout + Python
-> tools/safe_patch.py

GitHub connector only, preferred
-> permanent [remote-safe-patch-control] issue + v2 intent

connector preparation rollback
-> same permanent issue + v1 JSON request

permanent control issue unavailable
-> legacy remote-safe-patch PR-comment executor when usable

change is not narrow / target is protected
-> ordinary feature branch + PR
```

All routes preserve the same principle: a narrow semantic edit stays narrow, exact, reviewable, and fail-closed rather than becoming an unguarded reconstruction of a large current file.
