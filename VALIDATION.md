# Starter validation record

## G4 local continuation — 7 November 2026

- PASS: 116-test full suite, including 27 new G4 regressions; actual transcript at `runs/g4-tests-final-candidate.txt`.
- PASS: 48 original synthetic cases, six construction families/SOPs, 42 unambiguous author-rule candidates and six ambiguous cases with no unique candidate. All siblings remain in one provisional family/template partition.
- PASS: scope/time mismatches become unknown, explicit applicable failures remain contradictions, ambiguous rules are retained, record/availability witnesses fit the declared budget, and citations require exact delivered document locations.
- PASS: a gold-free scripted walkthrough executes 384 source transitions; separate scoring replays source responses and checks the 42 coauthored candidates. This is executable fixture consistency, not model/expert/pharma performance.
- PASS: blinded human-readable and JSON packets omit source IDs, pair orientation and authored decisions; blank intake is correctly INCOMPLETE. Completed structural intake in temporary unit fixtures cannot promote gold or establish human identity/independence. No completed expert rating was generated as a session artifact.
- Readiness remains false for independent review, adjudication and a reviewed reference lock. No paid API/model/network provider or new browser workflow is part of G4.

Evidence: `runs/G4-VALIDATION.json`, `runs/g4-walkthrough-final/`, `reports/g4-independent-review-v1-final/`, `reports/g4-review-intake-blank-final/` and `reports/g4-readiness-final/`. Original native/G3 source and earlier artifacts were preserved. See current STATUS.md for exact commands and remaining human work.

## G3 local continuation — 7 November 2026

- PASS: full 89-test suite, including 29 new G3 regressions; exact transcript at `runs/g3-tests-verified-v2.txt`.
- PASS: input-only segmentation/grouping and separate reference preparation on 607 documents, 606 source families and 10,319 original hypotheses. All characters/spans reconstruct; exact duplicates are grouped; broader near-duplicate independence remains unverified. Counterfactual pairs: zero.
- PASS: real local dev smoke on one source family/document, 17 hypotheses × 3 offline policies × budgets 0/1/4/20 = 204 dependent matrix episodes. Checkpoint after 4 transitions resumed from an active episode and completed 1,479 transitions with no paid/model calls.
- PASS: separate scoring/replay, cap/failure/pending denominators, one-action global stop, and one-byte source-exposure rejection. Reference/oracle results stay under evaluator/ and never appear in raw policy observations.
- Oracle feasibility is only the declared all-published-reference coverage proxy, not semantic/minimal evidence sufficiency. Full-source exposure for the selected dev document costs 20 credits; it is not a universal dataset budget.
- The native G1/G2 source hashes and old run compatibility were preserved. Existing CAPA/browser/API regressions are included in the 89-test suite. G3 is CLI/Python API only; no new browser integration/check is claimed for this increment.

Evidence: `runs/G3-VALIDATION.json`, `runs/g3-sequential-verified-v2/`, `runs/g3-action-cap-v2/`, `runs/g3-exposure-cap-v2/`. Earlier G3 iterations are preserved; final replay requires the frozen current source. See [STATUS.md](STATUS.md) for exact commands and next steps.

## Windows continuation — 7 November 2026

This supersedes the historical browser limitation below for this machine. It is engineering evidence, not pharmaceutical validation.

- PASS: initial 35 tests; final 60 tests in 2.186 seconds, including live HTTP and 25 new native-pipeline/metric regressions.
- PASS: Python 3.13.15, no added runtime dependency; JavaScript syntax check exit 0.
- PASS: 32-episode engineering smoke; original benchmark checksums/split counts, prepared-file hashes and cross-split document checks.
- PASS: offline full-context and document-local BM25 paths on one ContractNLI dev document / 17 hypotheses each; 12-item DrugQA prefix wiring smoke; separate evaluator reports. Pausing after item 5 resumed to 17 without duplicate calls. A 2-call cap stopped before call 3 and retained the 17-item score denominator.
- PASS: canonical DrugQA template equality against pinned source literals via AST inspection; downloaded source was not executed.
- PASS: actual Chromium desktop/mobile screenshots at 1440/390 px, relevant/irrelevant record requests, free reopening/idempotent duplicate POST, manual verdict, scripted completion, debrief, actual Markdown/JSON downloads and no horizontal document overflow.
- PASS: active response excludes gold/unrequested content; only requested D2 returned; early export/late mutation return 409. Missing favicon fixed; final console has 0 errors/0 warnings. Debrief now distinguishes missing submitted reference citations from records already retrieved.

Evidence: `runs/WINDOWS-VALIDATION.json`, `runs/browser/`, `runs/engineering-smoke.json` and four `runs/native-*-v2/` folders. Exact continuation commands are in [STATUS.md](STATUS.md). v1 outputs are retained as earlier pre-hardening artifacts. All fake runs use USD 0/no LLM tokens; they do not establish model quality, semantic support, independent review or domain validity. No real provider, native held-out inference or confirmatory analysis ran.

## Historical packaging checks

Date:7 November2026. Validation applies to the delivered starter; it is not a pharmaceutical validation dossier.

## Executed checks

| Check | Observed outcome |
|---|---|
| Python unittest discovery |35 tests passed, including live local HTTP workflows |
| Fresh repository ZIP extraction |35 tests passed again;32-episode engineering command completed from the extracted package |
| Engineering benchmark |32 deterministic episodes; repeated-run equality checked in test suite |
| JavaScript syntax |node --check passed |
| HTML/DOM contract |No parse errors;53 unique IDs; referenced IDs and local assets present |
| Evidence isolation |Unrequested content/gold excluded before terminal submission; cross-session isolation tested |
| Action validation |Unknown IDs, invalid citations, budget overflow, duplicate requests and terminal mutations tested |
| HTTP boundaries |Static path traversal, host/origin checks, body limits and malformed JSON tested |
| Native source preparation |Checksums verified; ContractNLI423/61/123documents and7191/1037/2091hypotheses; DrugQA11444items |
| Adapter separation |Whitelisted model fields; labels/explanations in separate evaluator files; altered bytes/path escape rejected |
| Literature PDF integrity |21 files parsed with page counts; first-page title/version checked |
| Regulatory PDF integrity |6 files parsed; draft/final status recorded separately |

## Browser limitation

A full browser render/click test was not completed. Local Chromium could not create required sockets; the supported browser connection had no usable originating context; the cloud browser could not reach local loopback. No visual acceptance claim is made. The owner's local Codex session should do one complete human workflow and a responsive layout check.

## What these checks do not establish

No measured model superiority, semantic entailment quality, pharmaceutical reference validity, human learning gain, real-world CAPA effectiveness, production security certification or regulatory compliance is claimed. The scripted policies were built with the fixtures; the demo is not a held-out scientific evaluation.

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m qa_war_room benchmark --output runs/engineering-smoke.json
python scripts/prepare_benchmarks.py --source benchmark-data
```

Frontend syntax checking requires Node only for that check; Node is not needed to run the app. Paper revalidation can use pypdf, which is not an app dependency.
