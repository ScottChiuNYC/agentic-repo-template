# AI Agent GitHub Workflow

## Purpose

Use GitHub as transactional shared state, not as an unstructured notebook or execution scratchpad.

The objective is deterministic repository state transitions with optimistic concurrency, exact-head validation, idempotent recovery, and complete post-merge verification.

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

## 1. Golden path

```text
READ latest main
-> RECORD exact base SHA
-> PLAN exact intended diff
-> CREATE one canonical task branch
-> WRITE only intended paths
-> VALIDATE content and diff
-> RECONCILE against latest main
-> OPEN one focused PR
-> VERIFY mergeability + required checks + exact head SHA
-> SQUASH MERGE exact validated head
-> VERIFY main
-> VERIFY applicable artifacts/publication
-> CLEAN branch/transaction state
-> DONE
```

Deviations are recovery paths, not alternative normal workflows.

## 2. Safety invariants

Every agent-initiated mutation MUST obey:

1. Never write directly to `main`, except the unavoidable first commit of an empty repository.
2. Never force-update `main`.
3. Never create noop/probe/placeholder repository files merely to test API behavior.
4. Never merge unresolved conflicts or knowingly failing required checks.
5. Merge only the exact PR head SHA that passed required validation.
6. Unknown write outcome is a read/reconciliation problem, not permission for blind retry.
7. A successful merge is not completion; main verification, applicable publication, and cleanup remain part of the transaction.
8. Preserve unrelated work and treat concurrent `main` advancement as normal optimistic concurrency.

## 3. Fixed preflight

Before creating a branch or performing a write:

1. fetch latest `main`;
2. record its exact commit SHA;
3. read task-relevant files from current repository state;
4. search for overlapping active branches/PRs when concurrency is plausible;
5. identify authoritative contracts and intended final state;
6. determine intended changed paths;
7. create one canonical task branch from the recorded SHA.

A conversation transcript or earlier fetched copy is not a substitute for current repository state.

## 4. One task, one canonical transaction

Each task MUST have one canonical working branch and, after PR creation, one canonical PR.

Do not casually create `-v2`, `-final`, or replacement branches after an ambiguous result. First rediscover actual state and recover the existing transaction.

A replacement branch MAY be created only when the existing transaction cannot safely continue. Superseded task-owned PRs/branches MUST then be explicitly cleaned.

## 5. Concurrency and main advancement

Multiple unrelated tasks MAY proceed concurrently. Each mutable task owns only its branch/PR, never `main`.

Before merge, reconcile the task against latest `main`:

- if intervening changes are unrelated, replay/rebase/update as needed and revalidate;
- if they overlap semantically, re-read current authority and recompute intended final state;
- never force an old patch over newer conflicting content;
- any change to the PR head after validation requires validation of the new head.

`behind main` does not automatically mean stale, and an old branch is not automatically safe to delete.

## 6. Mutation strategy

Choose the narrowest safe mechanism that matches the intended change:

```text
new file
-> normal create-file path

narrow existing tracked UTF-8 edit with local execution
-> Safe Patch

narrow existing tracked UTF-8 edit with connector-only execution
-> Remote Safe Patch

intentional whole-document rewrite
-> full replacement when the rewrite itself is the task
```

Read `safe_patch.md` and `remote_safe_patch.md` before using those paths.

A low-level full-blob API does not justify reconstructing a large current file for a small semantic edit.

## 7. Deterministic diff gate

Before opening a PR, verify:

- changed files match intended scope;
- no temporary/control/generated/unrelated files are present unless intentionally part of the task;
- no accidental deletions, renames, or formatting churn occurred;
- complete resulting file contents express the intended final state;
- required syntax, Markdown, build, test, or workflow validation passed.

Diff validation and content validation are separate gates.

For Markdown changes, follow `docs/WRITING_AND_MARKDOWN_RULES.md` and run the repository-required Markdown/math/link checks where applicable.

For workflow changes, validate the actual workflow behavior when practical; YAML parsing alone is not sufficient evidence.

## 8. PR and exact-head merge gate

After the branch passes validation:

1. open one focused non-draft PR unless the owner explicitly requests review-only/draft mode;
2. record PR number and current head SHA;
3. inspect final diff and mergeability;
4. confirm all required checks correspond to that exact head SHA;
5. immediately before merge, re-read PR head and latest relevant base state;
6. if head or materially relevant base state changed, revalidate;
7. squash merge using `expected_head_sha` or equivalent guard when supported.

A historical green run for an older SHA is not merge authority.

## 9. Post-merge verification

After merge:

1. verify the PR is actually merged;
2. verify intended content exists on `main`;
3. record final `main` SHA;
4. verify each applicable post-merge CI/publication/deployment step rather than inferring success from an unrelated umbrella status;
5. verify artifacts correspond to the intended run/SHA when metadata permits;
6. verify external publication such as Google Drive when configured;
7. verify automatic branch deletion or delete the task branch explicitly;
8. remove superseded task-owned transaction state;
9. confirm no unintended repository state remains.

If cleanup cannot be completed because of capability/permission limits, report it as incomplete rather than silently declaring DONE.

## 10. Transaction state model

A normal repository task conceptually moves through:

```text
PREFLIGHT
-> BRANCH_READY
-> CHANGES_WRITTEN
-> VALIDATED
-> PR_OPEN
-> PR_VERIFIED
-> MERGED
-> MAIN_VERIFIED
-> PUBLICATION_VERIFIED    # when applicable
-> CLEANED
-> DONE
```

An agent MUST NOT skip a state whose invariant has not been established.

This state model is conceptual and may be implemented by an external durable orchestrator; GitHub remains authoritative for GitHub-owned facts such as commits, refs, PR state, checks, merges, and artifacts.

## 11. Failure recovery and task-level idempotence

Individual API calls are not always idempotent. The task workflow SHOULD be.

For timeout, interruption, ambiguous tool result, or crash:

```text
UNKNOWN RESULT
-> READ actual branch / file / PR / main / workflow state
-> DETERMINE which invariant currently holds
-> ACT only if desired state is not already present
-> REVALIDATE
-> CONTINUE
```

Never blindly retry create/update/merge/close/delete after an unknown outcome.

A durable external orchestrator SHOULD persist logical workflow state, but after restart it MUST reconcile persisted state with real GitHub state before issuing another side effect.

## 12. Audit/remediation integration

Formal Essence audit/remediation follows `INDEPENDENT_PRE_FREEZE_AUDIT.md`.

Repository integration remains deterministic even when reasoning is multi-agent:

```text
parallel read-only audit round against exact SHA
-> canonical finding reconciliation
-> owner decisions if required
-> separate remediation transaction
-> PR / exact-head validation / squash merge
-> post-merge verification
-> next fresh audit round against new main SHA
```

Auditor findings or LLM assertions do not substitute for GitHub-state validation.

## 13. Branch hygiene

Task cleanup is mandatory. Automatic deletion of merged PR branches SHOULD be enabled for repositories using short-lived task branches, but agents MUST still verify cleanup.

Maintenance of unrelated old branches/PRs SHOULD be a separate explicit maintenance task. Do not opportunistically delete another task's state merely because it is old or behind `main`.

## 14. Definition of done

For a normal repository task, DONE requires all applicable conditions:

```text
intended change exists on main
required validation passed against the exact integrated change
focused PR was squash-merged
main was re-read and verified
canonical current-state artifact was re-read and is materially accurate
applicable CI/artifacts/publication were verified
source branch and task-owned transactional state were cleaned
no known task-scoped blocker remains
```

An edit, open PR, green historical check, or merge without required post-merge verification is not completion.
