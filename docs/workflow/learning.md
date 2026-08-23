# AI Learning Workflow

Use this workflow when the repository owner needs to learn or relearn a technical domain, paper, model, standard, API, or method well enough to reason independently rather than merely consume a summary.

Learning is not summarization. The target is durable mastery: the ability to reconstruct, verify, criticize, and generalize the material, then use it in research or implementation.

This workflow is intentionally adaptive. Validate it on real learning sessions and keep only the structure that improves learning efficiency.

## Core sequence

```text
Define target
-> Map prerequisites
-> Diagnose gaps
-> Select learning mode
-> Active practice
-> Verify
-> Compress
-> Test / generalize
-> Promote durable knowledge
```

## 1. Define the mastery target

Define what "learned" means before starting from page one. Prefer observable targets such as:

- explain the core mechanism and assumptions without notes;
- reconstruct the main derivation;
- implement the method and pass a numerical sanity check;
- compare competing methods and their failure modes;
- analyze an unseen variation correctly;
- decide whether the method belongs in the project's research or production path.

Keep each learning session focused on the smallest useful next target.

## 2. Map prerequisites

Build a compact dependency or knowledge map for the target. Reuse what the owner already knows and teach only prerequisites that actually block the next step.

Do not infer mastery from familiarity with terminology.

## 3. Diagnose gaps

Use questions, derivations, counterexamples, small calculations, code, or experiments to determine the current mastery level. A diagnostic should reveal what the learner can produce, not merely what looks familiar when shown.

## 4. Select the learning mode

Different knowledge types need different teaching loops. A topic may combine several modes.

- **Mathematical / model:** intuition -> derivation -> learner reconstruction -> critique -> limiting cases -> numerical verification.
- **Numerical / algorithmic:** derivation -> implementation -> convergence or benchmark -> failure analysis.
- **Software / system:** architecture map -> inspect the real system -> modify or debug -> explain trade-offs.
- **Literature / research domain:** source graph -> claims / mechanism / assumptions / evidence -> cross-source synthesis -> independent view.
- **Rules / regulation:** source hierarchy -> exact rule -> exceptions -> applicability checklist. Re-check current primary sources when rules may have changed.

## Mastery states

```text
Unknown
-> Recognized
-> Understood
-> Reproduced
-> Generalized
```

- **Recognized:** can identify the terminology, formula, interface, or main claim.
- **Understood:** can explain the mechanism, assumptions, and key logic.
- **Reproduced:** can reconstruct the derivation, implementation, or analysis without relying on the original presentation.
- **Generalized:** can analyze an unseen variation and explain which conclusions survive, which fail, and why.

Core research knowledge should normally reach at least **Reproduced**. Important foundations should preferably reach **Generalized**.

## Agent teaching behavior

The agent acts as tutor, research guide, and examiner, not as a summary machine.

1. Start each session by identifying the current mastery target, the learner's position in the dependency map, and the smallest useful next step.
2. For important derivations or mechanisms, ask the learner to produce the next step before revealing it. Prefer a targeted hint before a complete answer.
3. Adapt to the learner's response. Move forward when mastery is demonstrated; return to a prerequisite when it is not.
4. Periodically use an unseen question, variation, counterexample, implementation task, or numerical check to test transfer rather than recognition.
5. Distinguish primary-source claims, agent inference, owner hypotheses, and unresolved questions.
6. Return important claims to authoritative primary sources. A summary is not a substitute for evidence.
7. Do not reteach material the learner can already reproduce reliably.
8. When the owner is relearning their own prior work, treat the repository as durable external memory: reconstruct the reasoning from canonical artifacts without pretending that authorship implies current recall.

## Source discipline

Prefer, in order:

1. primary specifications, official documentation, papers, source code, or canonical repository derivations;
2. high-quality secondary explanations;
3. community discussion for experience reports and edge cases.

For repository PDFs, use the reference-ingestion protocol when durable page-level access is valuable.

## Learning workspace and promotion

Immature learning material may live under:

```text
learning/<topic>/
```

Typical contents include a roadmap, diagnostic questions, source map, scratch derivations, and small experiments. This is a staging area, not a permanent knowledge dump.

Promote mature, verified conclusions to the appropriate canonical location, for example:

```text
docs/research/...
src/...
tests/...
```

Use this progression:

```text
Learning
-> Mastery
-> Reusable knowledge
-> Research / implementation
```

Do not preserve every learning transcript. Preserve only what helps restore the mental model, records important rationale or verified results, or keeps unresolved questions visible.

## Relationship to repository artifacts

Keep exploratory learning separate from normative artifacts:

- **learning note:** questions, diagnostics, explanations, scratch derivations, and practice;
- **research note:** evidence, exploration, and unresolved research questions;
- **decision record:** a chosen direction and its rationale;
- **Essence:** an implementation-ready normative contract.

Do not freeze learning-stage uncertainty into an Essence merely to make progress look complete.

## Session closeout

At the end of a meaningful learning session, record only what is useful for continuation:

- current mastery state;
- what the learner can now reproduce;
- the smallest remaining gap;
- any misconception or failure mode worth remembering;
- the next diagnostic or practice target;
- any verified conclusion ready for promotion.

The next session should resume from this state rather than restart the topic from the beginning.
