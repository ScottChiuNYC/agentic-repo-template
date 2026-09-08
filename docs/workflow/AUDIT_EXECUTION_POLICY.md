# Formal Audit Execution Policy

## Purpose

This document defines who controls the executor/model used for formal independent audit work and how that choice is recorded and enforced.

The core distinction is:

> **Workflow semantics are executor-neutral; formal audit executor/model selection is owner-controlled.**

Executor neutrality means ChatGPT, coding agents, API workers, Steward, or another approved runtime may implement the same repository protocol. It does **not** authorize a dispatcher, worker, or platform to silently substitute one executor/model for another.

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

## 1. Scope

This policy applies to every formal independent Auditor slot, including pre-freeze audits, post-freeze verification audits, and any later certification round that relies on independent model judgment.

Reconciler and Remediator execution MAY also be constrained by owner-selected execution policy, but Auditor selection is the hard requirement because model/executor choice directly affects the epistemic evidence behind a PASS/FAIL certification.

## 2. Owner-controlled execution selection

Before any Auditor slot is dispatched, the durable round state MUST declare the requested execution policy for that slot.

At minimum, record:

```text
requested_executor
requested_model
model_selection_mode
allow_automatic_substitution
```

`model_selection_mode` is one of:

```text
exact
allowed_set
provider_auto
```

Semantics:

- `exact`: the slot MUST run on the requested executor and requested model identity. `allow_automatic_substitution` MUST be `false`.
- `allowed_set`: the durable round/slot state MUST record the complete owner-approved executor/model set and one preferred `requested_executor` / `requested_model` pair. If `allow_automatic_substitution = true`, the dispatcher MAY automatically choose or fall back to another member of that recorded set. If it is `false`, only the preferred pair may be launched automatically; another approved-set member requires a new durable owner/policy selection before dispatch.
- `provider_auto`: the owner explicitly delegates model selection to the named provider/runtime while retaining the requested executor/provider boundary. Provider-internal automatic model selection is intrinsic to this mode and is not a substitution. `allow_automatic_substitution` MUST be `false`; switching to another executor/provider still requires a new durable owner/policy selection.

Any other combination of `model_selection_mode` and `allow_automatic_substitution` is invalid configuration and MUST block dispatch.

`allow_automatic_substitution` never broadens the choices authorized by `model_selection_mode`. In particular, it cannot convert `exact` or `provider_auto` into an implicit fallback policy.

If the round does not contain a complete durable execution policy, a dispatcher MUST NOT infer one merely from whichever backend is easiest to launch.

A repository or orchestrator MAY maintain a persistent owner-approved default execution policy so the owner does not need to select models before every round. A round-specific owner instruction overrides that default.

## 3. No silent fallback

For formal audit work, automatic executor/model substitution is prohibited unless the durable execution policy explicitly permits it under the rules above.

In particular, the following are invalid under `model_selection_mode = exact`:

```text
ChatGPT -> Copilot
Copilot -> API worker
requested flagship model -> cheaper model
requested model -> provider_auto
requested exact model -> unknown/unverifiable model
```

If the requested executor/model is unavailable, over quota, unsupported by the current transport, or cannot be verified, the workflow MUST fail closed into an execution-blocked state rather than silently continue with a substitute, except for an explicitly authorized `allowed_set` fallback.

Recommended durable status:

```text
BLOCKED_REQUESTED_EXECUTOR_UNAVAILABLE
```

The owner or an already-authorized policy may then choose a replacement. The blocked state is an execution-policy condition, not an audit finding and not a scientific owner decision.

## 4. Requested and actual provenance

Every sealed Auditor result MUST record both requested and actual execution provenance.

At minimum:

```text
requested_executor
requested_model
model_selection_mode
allow_automatic_substitution
actual_executor
actual_model
```

For `allowed_set`, the durable round/slot record MUST also identify the complete approved set used for validation.

Where available, also record stable runtime evidence such as:

```text
provider
provider_run_id
agent_runtime
reasoning_setting
processing_mode
```

The `actual_model` field MUST use the strongest identity the execution platform can attest. A model name guessed from product branding, UI appearance, or prior behavior is not verified provenance.

If an exact-model round uses a backend that cannot attest the actual model, that slot does not satisfy the requested execution policy.

For `provider_auto`, the actual model SHOULD still be recorded when the provider attests it; absence of a specific model identity does not invalidate the slot when the owner explicitly authorized provider-level automatic selection and the requested provider/executor identity is verifiable.

## 5. Slot validity and reconciliation

Before a sealed raw result is counted toward the required Auditor set, the Reconciler or deterministic control layer MUST verify execution-policy compliance.

A slot is invalid when, for example:

- requested and actual executor/model do not match an `exact` policy;
- an actual choice is outside the durable `allowed_set`;
- an automatic move away from the preferred pair occurred with `allowed_set` and `allow_automatic_substitution = false`;
- provider automatic selection occurred without `provider_auto` authorization;
- `provider_auto` changed the requested executor/provider boundary;
- required provenance is missing or cannot establish compliance;
- a silent fallback occurred;
- the selection-mode / substitution-flag combination was invalid.

An execution-invalid slot is neither `PASS` nor `FAIL` evidence for the round. It MUST be excluded and replaced by a compliant fresh slot before the round can reach a canonical verdict.

Do not reinterpret an execution-policy violation as a substantive repository finding.

## 6. Heterogeneous and high-confidence rounds

Model diversity is an explicit round configuration, not a reason to substitute opportunistically.

A heterogeneous round MAY assign different exact policies per slot, for example:

```text
Auditor A -> ChatGPT / flagship-model-X
Auditor B -> provider-Y / model-Y
Auditor C -> provider-Z / model-Z
```

The same rule applies to larger near-freeze/final-verification rounds: auditor count and auditor diversity are independently controlled variables.

A dispatcher MUST NOT manufacture diversity by silently replacing an owner-selected homogeneous round with a mixed backend set.

## 7. Automation and owner interruption

This policy is compatible with full automation.

Preferred operating model:

```text
owner records a persistent execution policy
-> dispatcher applies it automatically to eligible rounds
-> workers execute only within that policy
-> requested backend unavailable
   -> use an explicitly authorized allowed_set fallback, or fail closed
-> genuine repository owner decision
   -> WAITING_FOR_OWNER
```

The owner should not need to copy prompts merely to preserve model choice. The orchestrator owns enforcement; the durable round state owns the requested selection.

A `supervised` orchestration mode MAY require owner approval at additional transitions. A `full_auto` mode MAY continue all non-owner-decision transitions automatically, but `full_auto` still MUST NOT override the configured audit execution policy.

## 8. Bootstrap prompts

Bootstrap prompts SHOULD remain short.

When the durable round-control record already contains the complete requested execution policy, the prompt need only identify the role and durable workflow identity. A transport MAY echo the requested executor/model in the prompt when that helps bind the launched runtime, but the prompt copy is not the authority; the durable round record is.

A worker MUST NOT treat a prompt-level executor/model string as permission to ignore a conflicting newer durable owner instruction.

## 9. Dispatcher responsibilities

A dispatcher/orchestrator that launches formal audit workers MUST:

1. read the current owner-approved execution policy;
2. validate the selection-mode / substitution-flag combination before launch;
3. bind each slot to its requested executor/model and any complete `allowed_set` before launch;
4. refuse unsupported silent substitution;
5. record launch provenance and stable runtime identity where available;
6. reconcile unknown launch outcomes before retry;
7. preserve sibling-auditor isolation;
8. require provenance compliance before marking a slot valid and complete.

The dispatcher owns execution eligibility and launch policy. The Auditor owns substantive independent review. Neither role may silently rewrite the other's contract.

## 10. Historical evidence

Historical audit rounds remain historical evidence under the policy that governed them at execution time.

Missing historical model provenance MUST NOT be retrospectively invented. If a later owner confidence requirement demands a known exact model or a different executor family, run a new verification round against an explicitly frozen SHA instead of relabeling the historical round.

## 11. Default safety rule

Unless durable owner policy explicitly says otherwise, formal audit execution is fail-closed:

```text
selection mode: exact when an exact executor/model was requested
allow_automatic_substitution: false for exact and provider_auto
silent executor/model substitution: prohibited
unknown actual model under exact mode: invalid slot
```

This safety rule prevents convenience, availability, or orchestration implementation details from silently changing the epistemic basis of a formal repository certification.
