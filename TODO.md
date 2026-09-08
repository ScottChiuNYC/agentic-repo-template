# ART TODO

這份文件只記錄 ART 本身尚未定案的設計問題與後續工作，不是 agent 每次執行任務時必須載入的 authority，也不應逐步膨脹成另一份 operating protocol。

## Protocol compression / attention budget

### 背景

目前 ART 的 repository protocol 已經相當完整，而且對正常 task 的 Definition of Done 其實很明確：agent 應自行完成 branch、PR、exact-head validation、squash merge、post-merge verification、artifact/publication verification 與 cleanup，最後才向 owner 回報完成。

實際使用仍觀察到一種 failure mode：即使規則已寫清楚，agent 在長任務中仍可能於 `PR_OPEN`、`CHECKS_RUNNING` 或 `MERGED` 等 intermediate state 提前把控制權交回 owner，而沒有一路執行到 publication verified / cleaned / done。

這比較像 execution-compliance / attention-budget 問題，而不一定是 specification gap。大型 context window 能容納完整 protocol，不代表模型在長 conversation、大量 tool output、review remediation 與 workflow monitoring 中，能始終給每一條 operating rule 足夠高的 attention。

### 待研究方向

- [ ] 評估 ART 是否已超過「規則越完整越可靠」的甜蜜點，開始因 active protocol 過長而降低執行可靠性。
- [ ] 將 agent-facing hot path 壓縮成極短 execution contract，例如：

  ```text
  READ -> BRANCH -> EDIT -> VALIDATE -> PR -> REVIEW -> SQUASH MERGE
       -> VERIFY MAIN -> VERIFY PUBLICATION -> CLEAN -> REPORT
  ```

- [ ] 明確區分：
  - **hot-path contract**：每個 mutation task 都必須保持在 attention 中的少量 invariants；
  - **reference protocols**：只有進入特定 state / task type 時才讀取的詳細規則。
- [ ] 研究 state-scoped loading：例如進入 PR/review、post-merge publication、audit 等 state 時，才載入對應 workflow 文件，而不是每次把整套 operating manual 都當 active instructions。
- [ ] 避免用更多重複的「IMPORTANT / MUST NOT REPORT EARLY」文字修補 compliance failure；若規格已清楚，優先減少 cognitive load 或增加 deterministic enforcement。
- [ ] 評估將 transaction state machine 外部化給 Steward / orchestration layer：只有到 `PUBLICATION_VERIFIED -> CLEANED -> DONE` 才允許產生成功回報，讓「不能提早宣告完成」成為 machine-enforced invariant，而不是只靠模型記住 prompt。
- [ ] 用實際 repo mutation failure cases 做 regression tests，特別測試長 conversation、PR review remediation、slow CI / PDF build、Google Drive publication 等情境。

### 設計原則

目標不是刪除詳細 protocol。詳細規格仍應保留作為 durable authority、edge-case reference 與 audit contract；要壓縮的是**每個 execution turn 必須同時維持在 working attention 裡的規則集合**。

換句話說：

> ART 應盡量把「要求 LLM 記住一整本 operating manual」改成「一個很小的 state machine；每個 state 只暴露當下必要的 contract」。

## Single dispatcher/orchestrator ownership

### Problem

ART's audit/remediation semantics already aim for low owner interruption, but execution ownership is still ambiguous in practice. Different role agents may independently initialize the next round, create raw-result slots, dispatch auditors, continue remediation, or instead ask the owner to copy prompts manually. GitHub mutations performed through an owner-authorized connector may also appear under the owner's identity, making it difficult to reconstruct which role or runtime initiated a transition.

The result is semantically valid but operationally inconsistent behavior: some audit loops continue automatically while others stop for manual routing, and the owner cannot reliably tell why a durable workflow object was created.

### Proposal

Introduce one explicit **Dispatcher / Orchestrator** as the only role allowed to advance the audit/remediation state machine and spawn downstream workers. Auditor, Reconciler, and Remediator become pure workers that publish their own durable completion state but do not independently decide or initiate the next workflow transition.

Target behavior:

```text
remediation integrated + publication verified
-> Dispatcher initializes next exact-SHA round and isolated auditor slots
-> Dispatcher launches auditors
-> all required slots SEALED
-> Dispatcher launches Reconciler
-> canonical FAIL with auto-remediable findings only
-> Dispatcher launches Remediator automatically
-> canonical owner decision required
-> WAITING_FOR_OWNER and interrupt owner once
-> durable owner resolution
-> Dispatcher resumes automatically
-> canonical PASS
-> mechanical freeze writeback + publication verification
-> DONE
```

Worker boundaries should be explicit:

- **Auditor**: inspect the immutable audit SHA and seal only its assigned raw-result slot.
- **Reconciler**: consume sealed slots and publish the canonical verdict/findings/owner-decision set.
- **Remediator**: implement only the canonical remediation transaction and publish durable completion evidence.
- **Dispatcher / Orchestrator**: observe durable state, enforce transition preconditions, choose/launch executors within the owner-controlled execution policy, and advance the state machine.

Owner interruption policy should be a first-class runtime mode. A likely default is `full_auto`, where only genuine owner-decision or owner-only-action states interrupt the owner; a `supervised` mode can require approval at selected transitions for debugging or high-risk repositories.

Every machine-created durable object should carry reconstructable provenance where the transport permits it, for example `created_by_role`, `trigger`, `executor`, `parent_round`, and `dispatch_id`. The objective is that a future reader can tell not merely who GitHub attributes the mutation to, but **which workflow role created it and why**.

Formal audit executor/model choice is no longer an unresolved part of this proposal: `docs/workflow/AUDIT_EXECUTION_POLICY.md` makes it owner-controlled and fail-closed. The remaining dispatcher work is to enforce that durable policy rather than silently select or substitute a convenient backend.

### Questions to resolve before promotion into protocol

- [ ] Define the canonical machine-readable workflow states and transition preconditions owned by the Dispatcher.
- [ ] Decide which transitions may be fully automatic and which repository classes require supervised mode.
- [ ] Define durable provenance fields and how they map onto GitHub issues/PRs versus an external orchestrator state store.
- [ ] Ensure crash/restart recovery is idempotent: the Dispatcher must reconcile actual GitHub state before creating or launching anything new.
- [ ] Enforce auditor isolation structurally where possible rather than relying only on prompt discipline or issue discoverability.
- [ ] Keep workflow semantics executor-neutral while formal audit executor/model selection follows owner-controlled durable policy; the Dispatcher must never treat backend availability as substitution authority.
- [ ] Decide how ART defines the generic state-machine semantics while Steward (or another runtime) implements dispatch, monitoring, retries, and owner notifications.
- [ ] Use SABR-Cheyette's recent mixed manual/automatic audit loops as a concrete regression testcase for the design.

This is a proposal, not current normative ART policy. The desired end state is that the owner normally sees the audit/remediation loop only when a genuine owner decision is required or when the loop reaches its final verified outcome.

## Adaptive independent-auditor count

### Proposal

Independent pre-freeze audit rounds need not use the same auditor count at every convergence stage. Consider an adaptive policy:

```text
ordinary convergence rounds: 3 auditors
near-PASS confirmation:      5 auditors
final freeze candidate:      7-10 auditors
```

The goal is to spend additional independent-review capacity when marginal coverage is most valuable. Early rounds already known to contain blockers may gain little from expanding every round to ten auditors, while a near-freeze candidate benefits more from a larger search for residual blind spots.

### Questions to resolve before promotion into protocol

- [ ] Define objective escalation signals, such as canonical finding count, overlap ratio across auditors, new owner-decision count, or recent rounds with zero/near-zero unique findings.
- [ ] Preserve the existing invariant that all auditors in one round evaluate the same immutable SHA and remain isolated from sibling findings before sealing.
- [ ] Measure diminishing returns from additional auditors, including correlated blind spots and reconciliation cost.
- [ ] Decide how owner-controlled executor/model configuration should express model/configuration/reasoning diversity when the execution environment supports it.
- [ ] Validate the proposal empirically across several real audit-remediation loops before making it normative ART policy.
