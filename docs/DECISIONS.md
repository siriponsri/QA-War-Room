# Decision record

| ID | Decision | Status / reason |
|---|---|---|
| D01 | Manufacturing GMP is the first domain | Explicit owner selection in this conversation |
| D02 | Solo implementation; product and paper in parallel | Explicit owner requirement |
| D03 | Published open benchmarks first | Explicit owner requirement; native tasks retained |
| D04 | CAPA closure/effectiveness evidence is the first narrow task | Proposed default grounded in the chosen domain; editable after review |
| D05 | English technical docs/UI, Thai owner guide | Starter assumption for international paper/Codex use |
| D06 | ICH Q10 + public US/EU references as research context | Starter assumption; not a claim of Thai/PIC/S jurisdiction equivalence |
| D07 | No paid inference in the delivered starter | Budget not specified; offline work remains useful |
| D08 | Local-only demonstration | Hosting, authentication and real eQMS integration are later |
| D09 | Keep literature PDFs outside public source | Repository is public; paper/data/code rights differ |
| D10 | Original synthetic cases are engineering fixtures | Not real manufacturing records or reviewed research gold |
| D11 | Same-model roles are policies, not independent expert auditors | Prevents inflated expertise and replication claims |
| D12 | RL and operational twin deferred behind evidence gates | Avoids unnecessary scope and untested novelty |
| D13 | Repository inspected but no remote changes made | Package is ready for owner/Codex to import; no silent publication |
| D14 | Code/data licensing remains an owner decision | No third-party license is imposed on the owner's original work |
| D15 | Continue G3 locally/offline without paid APIs, preserving input/gold isolation and tests | Explicit owner instruction, 7 November 2026 |
| D16 | Continue G4 locally/offline: Manufacturing GMP cases, rubric and independent-review plan; no paid APIs | Explicit owner instruction, 7 November 2026; actual external review not performed |
| D17 | Continue G5 locally/offline: prospective plan and analysis pipeline, no paid APIs; do not assume completed independent review | Explicit owner instruction, 7 November 2026; engineering lock separate from refused scientific lock |
| D18 | Continue G6 locally/offline: manuscript draft and reproducibility package, no paid APIs; no assumed independent review or confirmatory results | Explicit owner instruction, 7 November 2026; local engineering rehearsal only, no publication or new license assignment |
| D19 | Add a live LINE-style chatbot and a separate modern minimal dashboard, GPO-inspired green/white, Light/Dark, Thai/English, no-code-friendly main flows | Explicit owner steering during G6, 7 November 2026; offline rule-based live actions, no paid LLM or exact official brand/affiliation claim |
| D20 | Pause Codex implementation and hand frontend refinement to Claude first | Explicit owner request, 7 November 2026; transfer documents only, backend/research/model continuation awaits owner direction |
| D21 | Add an AI settings page: six providers (Typhoon, Anthropic, OpenAI, Google Gemini, OpenRouter, Ollama), keys stored only in a local git-ignored file and shown masked, connection test through free account/model-list endpoints; live rooms still do not use any model | Explicit owner choice, 7 November 2026 (options: settings + test, local server file); D07 no-paid-inference still holds for room runs |

## Questions that improve the next milestone, without blocking this package

1. Which jurisdiction and setting should the first eventual pilot address: Thai/PIC/S, US FDA, or EU? The initial research context can stay ICH-based, but operational claims need a precise scope.
2. Can the owner obtain independent review from a manufacturing QA/CAPA practitioner for a blinded subset? If not, the first study must stay a constructed-environment evaluation.
3. What compute/API spending cap and preferred providers apply to real benchmark runs?
4. Is there an eventual source of de-identified manufacturing case packets with documented permission? The first phase does not require them.
5. Is the intended first customer an individual trainee/training provider or a manufacturing QA team? This changes packaging and pilot outcomes.
6. Should the project license be permissive, dual-licensed/open-core, or reserved initially? Decide before inviting reuse, not after copying incompatible dependencies.

These are decision points, not a request to stop local development. Record future owner answers here and do not ask the same question again.
