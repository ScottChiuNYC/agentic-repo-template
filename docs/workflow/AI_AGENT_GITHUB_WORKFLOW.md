# AI Agent GitHub Workflow

Use GitHub as a transactional shared state system, not as an unstructured notebook.

## Default transaction

```text
read main
-> define final diff
-> create feature branch
-> mutate only intended paths
-> open one focused PR
-> validate exact head SHA
-> review semantic diff
-> squash merge exact validated head
-> re-read main
```

## Before mutation

1. Read current `main` and task-relevant files.
2. Search for overlapping open PRs/branches when concurrency is plausible.
3. Record the base/head SHA used for the change.
4. Decide which files are in scope before writing.

Do not overwrite or stage unrelated work.

## Branch and PR rules

- Never write directly to `main`, except the unavoidable first commit of an empty repository.
- Use a task-specific branch.
- Prefer one PR per logical outcome.
- PR text should state purpose, material behavior changes, validation, and known limitations.
- Do not create duplicate PRs for the same branch.

## Exact-head validation

A green historical run is not sufficient. Before merge:

1. read the PR's current head SHA;
2. confirm required validation ran against that exact SHA;
3. confirm the PR remains mergeable against the intended base;
4. inspect the final diff;
5. merge using the exact expected head SHA when the API supports it.

If the head moved after validation, validate again.

## Concurrency

When `main` moves while a task is in flight:

- compare the new base with the task branch semantically;
- do not assume an old clean merge is still safe;
- rebase/update only when required;
- rerun validation after any head change.

For publication workflows, use concurrency groups that cancel obsolete runs for the same PR/ref when newer commits supersede them.

## Narrow edits

For one narrow exact-text change to an existing tracked UTF-8 file, prefer `tools/safe_patch.py` when possible. It provides:

- protected-branch rejection;
- exact expected-HEAD guard;
- unique anchor requirement;
- changed-line budget;
- syntax/Markdown validation;
- atomic write and rollback.

For connector-only mutation, use Remote Safe Patch instead of broad write access. See `remote_safe_patch.md`.

## Merge

Prefer squash merge for focused task branches. Supply the expected PR head SHA if supported so a concurrently modified branch cannot be merged accidentally.

After merge:

- verify `main` contains the intended result;
- verify automatic branch deletion if configured;
- inspect post-merge publication or deployment workflows when applicable.
