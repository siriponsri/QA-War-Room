# Reproducibility and run records

## Delivered reproducible artifacts

The offline app uses deterministic synthetic records and scripted policies. The source snapshots have pinned commits and SHA-256 file checksums. Native model-input preparation is separate from evaluator outputs. The literature download manifest records actual acquisition status.

The starter's tests/engineering runner establish software behavior only. No LLM experiment, domain validation or performance claim is contained in those checks.

G5 now implements separate engineering `LOCK.json`, `manifest.json`, hash-chained `events.jsonl`, checkpoint/resume, exact source replay and evaluator-only analysis. The frozen matrix is reconstructed from public inputs on every load, preventing a silently reduced denominator. `ANALYSIS.json` records source/run/evaluator/code and generated-output hashes. See [G5_EVALUATION_PLAN.md](G5_EVALUATION_PLAN.md) for exact commands and current artifact layout; the generic future layout below is not a claim about existing files. Scientific reference/model/margin locks remain unavailable pending actual review and adjudication. A confirmatory request writes a refusal, not a lock.

## Required manifest for every future model run

Record run_id, start/end UTC, source commit and dirty status, dataset version and hashes, independent family IDs and split, task/adaptation version, code/environment version, model/provider/version/date, prompt/system/action schema versions, retrieval index/version, chunking, random seeds, decoding, token/context limits, evidence budget and cost schedule.

Also record every request, delivered record ID/version/span, refused/unavailable response, action validation failure, retry, token count, latency, pricing basis and terminal result. Preserve failed episodes. Do not store raw API keys, credentials or unnecessary company records.

## Evaluation controls

1. Freeze splits before transforms; keep source/counterfactual/translation siblings together.
2. Keep an immutable raw source snapshot. Transform into new files with a recorded script.
3. Prevent gold labels and reference explanations entering model input or retrieval.
4. Preserve official metric denominators; separately report abstention and execution failures.
5. Record independent groups as well as rows/turns/repeated runs.
6. Calibrate and choose thresholds on development data only.
7. Freeze confirmatory comparison and success criteria before unblinding.
8. Generate figures/tables from raw outputs, with a trace back to the run manifest.
9. Maintain both planned and actual deviations from protocol.
10. Publish only material for which redistribution is permitted, with attribution and sensitive-data review.

## Contamination and public benchmarks

Public evaluation data may have appeared in model pretraining. Separation at runtime prevents one form of leakage but cannot establish absence of pretraining contamination. Acknowledge that limitation. Newly authored held-out families and controlled counterfactual tests can provide complementary evidence; they must themselves be screened for trivial cues and generation bias.

## Future artifact layout

```text
runs/<run-id>/manifest.json
runs/<run-id>/episodes.jsonl
runs/<run-id>/costs.jsonl
runs/<run-id>/failures.jsonl
runs/<run-id>/metrics.json
runs/<run-id>/analysis/
```

This layout is proposed. The delivered engineering CLI writes one JSON report. Do not describe the full research pipeline above as already implemented.

## Publication archive

G6 now implements a **local preparation bundle**, described in [G6_REPRODUCIBILITY.md](G6_REPRODUCIBILITY.md): deterministic source/environment/run/evaluator ZIPs, source-replayed manuscript facts, checksums and a fresh-directory rehearsal. It excludes third-party PDFs/raw external data and keeps gold/terminal outcomes outside environment inputs. It has no public deposit, license assignment, scientific results, independent review or submission authorization. The requirements below still apply before a future publication archive.

Before submission, produce an immutable release containing permitted code, data manifests or datasets, exact environment, analysis scripts, a data dictionary, model access requirements, evaluation commands, expected output schemas and actual raw results. Obtain a persistent identifier if appropriate. Keep training/development/test use explicit. If models are external services, record the access date and discuss reproducibility limits.
