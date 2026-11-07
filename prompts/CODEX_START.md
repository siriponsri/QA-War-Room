# Copy this prompt into Codex

You are continuing my **QA War Room** project in this repository. I am building it as a **solo project**, with the product and a pharmaceutical journal study in parallel.

The chosen first domain is **Manufacturing GMP**, focused on evidence for deviation/CAPA closure and effectiveness. The requested roles are user-01, user-02, auditor-newbie-01, auditor-newbie-02, auditor-expert-01, auditor-expert-02. They are role/policy identifiers, not proof of expertise.

Read AGENTS.md, GOAL.md, STATUS.md, PLAN.md, HANDOFF_TO_CODEX.md and docs/DECISIONS.md. Inspect the existing runnable offline starter and preserve useful work. Run the documented tests and engineering smoke runner, then check the UI locally.

Continue autonomously with the next concrete milestone: verify the published benchmark adapters and build a reproducible **native benchmark runner** with a narrow model interface, a deterministic offline adapter, source-preserving metrics, strict input/gold separation, resumable logging and explicit token/call/cost caps. Use ContractNLI and the authoritative Sino-US-DrugQA release according to DATASET_PLAN.md. Do not claim native benchmark scores until actual runs have occurred.

Then implement the simplest grounded single-agent baselines and the separately versioned sequential evidence-acquisition task. Compare multiple roles only under fair information and compute budgets. Use the pharmaceutical case specification and research protocol to prepare the later Manufacturing GMP study; do not claim the existing eight synthetic cases are a validated research dataset.

Complete authorized reversible local work without stopping after a plan. If credentials, spending authorization or a consequential owner decision is missing, finish all useful offline work, record the specific blocker and ask one focused question. Do not deploy, push remote changes, send messages, use company records or start paid jobs unless I have authorized that action. Never invent results, source citations or pharmaceutical validation.

Keep STATUS.md updated so another Codex session can continue. At each milestone report implemented behavior, meaningful tests, actual result paths, limitations and next actions. If the data show no multi-agent advantage, report that and preserve the simpler product.
