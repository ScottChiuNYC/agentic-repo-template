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

