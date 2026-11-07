# Open dataset and benchmark plan

**Checked 7 November 2026.** Dataset suitability is task-specific. There is no verified ready-made open dataset in this package containing complete pharmaceutical manufacturing CAPA audit packets with independent reference decisions. The project starts with published open tasks, then builds a clearly named pharmaceutical extension.

## Included original data snapshots

This Windows starter bundle contains `benchmark-data/` inside the local project root, excluded from Git. Original dataset bytes and license notices are included.

| Source | Included files and verified counts | Version | Intended role |
|---|---|---|---|
| ContractNLI [P05] | Original JSON: 423 train, 61 dev, 123 test documents; original license | gh-pages commit `eced6528dd3c1d14d73f9a87df8f7bdbc03126f9` | Native document NLI + evidence localization, then separately adapted sequential task |
| Sino-US-DrugQA [P04] | Authoritative bilingual `all.jsonl`: 11,444 items; 4,571 raw category Drugs; card + license | main commit `cd026a27a5e039863de9080b8d7d95acaf1f5a39` | Native pharmaceutical regulatory knowledge evaluation, not audit closure gold |

Original source file checksums and sizes are in `benchmark-data/SOURCE_MANIFEST.json`. The ContractNLI archive also contains individual source PDFs; only original JSON files and the license are included here. No source text or labels in those JSON files have been rewritten. DrugQA is the paper's original bilingual release, not its translated English companion.

Run `python scripts/prepare_benchmarks.py --source benchmark-data` to verify bytes and create model-input files separate from evaluator labels. This command is data preparation; it does not evaluate an LLM or reproduce a published score.

## ContractNLI: native task first

The publication defines document-level entailment, contradiction and NotMentioned classification with evidence spans over contracts. The 17 hypotheses are fixed across documents. Preserve the official document splits and original label strings. Do not describe results as generalization to arbitrary unseen audit clauses.

Native evidence metrics include the paper's span-ranking evaluation, including micro mAP and precision at recall 80; use its exact definitions and relevant original code before claiming reproduction. The G1/G2 offline increment now implements the reported metric subset, with the original inputs/references preserved; it is not a reproduced LLM score. G3 is a separately named sequential adaptation. G4's original synthetic Manufacturing GMP draft is described in [MANUFACTURING_CASE_PACK.md](MANUFACTURING_CASE_PACK.md) and has no independent domain validation yet.

An interactive adaptation might reveal document spans/chunks under a budget. Its score is a new score: the official benchmark supplies the full document. Also, NotMentioned is a whole-document relationship, whereas an agent not having read enough is an observation state. Keep those concepts separate.

Sources: [paper](https://aclanthology.org/2021.findings-emnlp.164/), [project](https://stanfordnlp.github.io/contract-nli/), [repository](https://github.com/stanfordnlp/contract-nli).

## Sino-US-DrugQA: domain knowledge, not a GMP case benchmark

The paper evaluates regulatory MCQs across US and Chinese sources. It reports a release of 10,122 pass and 1,322 borderline items, with independent expert review on defined cohorts rather than verification of every provision. Its source versions are valid as of December 2025. Neither the legal correspondence nor scores establish applicability to Thai/PIC/S practice.

The checked card reports 2,573 Manufacturing & Quality items across all object domains, but explicitly states that public records **do not include a per-item functional_subdomain field**. Thus 2,573 cannot be described as 2,573 pharmaceutical GMP audit cases, and the intersection Drugs ∩ GMP cannot be reconstructed directly from a released official tag. A new tagging protocol or an author-provided mapping would be required.

There is no official training split. Treat the release as evaluation-only in this project. Do not use reference answers/explanations for RL, prompt tuning or answer-bearing RAG. Native zero-shot input should match the paper's conventions; source retrieval is a separately labeled condition. Report invalid predictions in the denominator. A Drugs subgroup is a declared subgroup, not a reproduction of the whole benchmark.

Sources: [paper](https://doi.org/10.1371/journal.pone.0343858), [dataset card](https://github.com/DodgeLU/Sino-US-DrugQA/blob/cd026a27a5e039863de9080b8d7d95acaf1f5a39/DATASET_CARD.md).

## Optional additions

| Dataset | Why it may help | Conditions and limits |
|---|---|---|
| SciFact [P06] | Scientific claims and supporting/refuting evidence sets | Public train/dev gold; original test gold withheld. Claims/evidence CC BY 4.0, abstract corpus ODC-By. A local development evaluation is not an official hidden-test result. |
| ACE / COMPACT [P07] | Cross-clause enterprise compliance; optional graph reasoning baseline | Contracts originate in CUAD and ContractNLI. Source-document overlap can leak across otherwise separate datasets. Inventory overlap before splitting; not pharmaceutical data. |
| LabSafety Bench [P20] | Optional adjacent laboratory risk knowledge if scope later expands | Not Manufacturing GMP CAPA evidence. Preserve paper/data version; do not mix different release counts or repeated sampled items. |
| IntelliAudit [P08] | Related workflow and realistic heterogeneous audit artifacts | Do not assume released artifacts contain adjudicated gold labels. IT audit controls are not pharma effectiveness criteria. |

References: [SciFact repository](https://github.com/allenai/scifact); [ACE repository](https://github.com/FujitsuResearch/Fujitsu-Assessing-Compliance-in-Enterprise-Dataset); [LabSafety repository](https://github.com/YujunZhou/LabSafety-Bench); [IntelliAudit repository](https://github.com/allyftw/IntelliAudit-Benchmark).

## Licensing and provenance

Included datasets declare CC BY 4.0; retain their original notices, authors, source links and modification statements when redistributing derived files. Regulatory texts, paper PDFs, model outputs and code have separate rights. Commercial incorporation requires reviewing the specific materials actually ingested, not relying on a code repository's license.

The project has not copied ISO standards or private manufacturing records. Public FDA warning letters are potential case inspirations, but they are selective findings rather than complete records of both compliant and noncompliant audits. Never treat absence of a finding in a letter as evidence of compliance.

## Split and leakage rules

Keep all variants of a source document, template, matched case pair and derived paraphrase together. For cross-source experiments, normalize/hash source documents and check exact and near duplicates. Freeze groups before model-specific tuning. Report the number of independent groups, not only the number of episodes.

The demo's eight cases share two templates. They are unsuitable as an independent held-out effectiveness sample. No scientific train/test split is claimed for them.

## Planned adapter acceptance criteria

- Source checksums match; IDs are unique; official counts and label sets are preserved.
- Only whitelisted fields enter model prompts.
- Gold spans, explanations and reference actions exist only in evaluator artifacts.
- No silent truncation, schema changes, missing-row exclusions or changed denominator.
- Source IDs map every transformed task to original records.
- Retrieval, chunking and tokenization versions are recorded.
- Official metrics are independently checked on known small examples before a benchmark claim.
- Derived interactive tasks use a new version and explicit observation/action costs.
