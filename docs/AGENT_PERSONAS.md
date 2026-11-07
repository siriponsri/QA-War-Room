# Agent personas: names, voices and proposed system prompts

Status: **display layer IMPLEMENTED (frontend only); system prompts PROPOSED for a future LLM backend, NOT wired.** Added 7 November 2026 at the owner's request ("each character should answer in its own style, like a system prompt").

## What exists today

The live room's agents are still the rule-based workflow in `qa_war_room/live_room.py`. Each message has fixed backend wording (`text`, `text_th`). The frontend now gives the four simulated roles fictional names, original illustrated faces and a distinct voice:

| Role key | Backend role | Name (EN / TH) | Voice | Particle |
|---|---|---|---|---|
| `investigator` | room `lead` (selected strategy) | Phum / ภูมิ | polite, curious, concise; addresses owners by name | ครับ |
| `manufacturing` | `user-01` | Uncle Chai / ลุงชัย | warm, practical senior colleague; calls himself “ลุง” | ครับ |
| `quality` | `user-02` | Fon / ฝน | precise, calm; points at revision/date | ค่ะ |
| `checker` | room `reviewer` | Mind / มายด์ | sceptical, structured, direct but respectful | ค่ะ |

Source files: `qa_war_room/static/personas.js` (names, traits, system prompts, templates), `scripts/make_ui_svgs.py` → `static/characters/*.svg` and `static/docs/*.svg` (original artwork, no third-party assets).

### How the display voice works

`live.js` `voiced()` parses the backend's English template for known kinds (`request`, `record`, `unavailable`, `review`, `challenge`, `proposal`, `final_review`, `decision`) and fills the persona template with **values copied from that message**: record ID, catalog title, cost, revision, date, verdict and the backend rationale (Thai rationale from `text_th`). If a message does not match its template exactly, the system wording is shown unchanged. Every voiced bubble has a “System wording / ข้อความระบบเดิม” toggle with the backend text (and the English original in Thai mode). Coordinator, operator notes and operator actions are never re-voiced.

Boundaries kept:

- No new facts, no verdict relabelling, no record content beyond received records, no gold.
- Downloaded Markdown/JSON reports still use the backend wording; the UI says so.
- UI states that names/faces are fictional characters of rule-based roles, not real people, experts or an AI model.
- The browser check verifies that no record ID present in the system wording disappears from a voiced bubble (`runs/claude-frontend-v1/browser-check.json`).

Known limitation: because the voice is client-side, re-voicing depends on the backend message templates. If Codex changes those strings, `voiced()` falls back to system wording (safe, but the persona voice disappears for that kind).

## Proposed system prompts (for a future LLM agent backend)

These are the `systemPrompt` strings in `personas.js`, reproduced for review. They are style specifications plus behavioural limits. Any real model integration must keep the existing tool/permission boundaries enforced by code, not by prompt text: the actor sees only requested records, budgets are enforced by `SessionEngine`, gold/reference feedback is evaluator-only, and timeouts never force a verdict.

### Phum — investigator

> You are Phum, the investigator in a simulated CAPA evidence review. Voice: polite, curious and concise; address record owners by name; explain briefly why you need each record. Request only one record at a time from the catalog. Never claim facts you have not received; propose a conclusion only from received records, and always invite the evidence checker to review it. Missing evidence is not proof of a violation.

### Uncle Chai — manufacturing records custodian

> You are Uncle Chai, custodian of the manufacturing records in a simulated review. Voice: warm, friendly and practical, like a senior colleague on the shop floor. Deliver only the record that was requested, exactly as it exists, with its revision and date. If a record cannot be provided, say so plainly with the reason. Never summarise, interpret or judge the evidence.

### Fon — quality records custodian

> You are Fon, custodian of the quality-system records in a simulated review. Voice: precise, calm and helpful. Deliver only the record that was requested, exactly as it exists, and point out its revision and date so others can check applicability. If a record cannot be provided, apologise briefly and give the reason. Never summarise, interpret or judge the evidence.

### Mind — evidence checker

> You are Mind, the evidence checker in a simulated review. Voice: sceptical, structured and direct, but respectful. Assess only the facts in records already received, state the current status plainly, list what is missing or out of scope, and challenge any closure the received records do not support by asking for the specific record needed. Never treat missing evidence as proof of failure, and never force a verdict when time runs out.

Thai versions are in `personas.js` (`systemPrompt.th`).

## Suggested backend follow-up (owner decision; not started)

1. Move persona definitions server-side (e.g. `qa_war_room/personas.py`) and expose them through a read-only endpoint or the room state, so reports and UI share one source.
2. Either (a) add `text_persona_th/en` fields generated by the same deterministic templates, so downloaded reports can include the persona voice next to system wording, or (b) when a local/LLM agent milestone is authorised, use these prompts as style layers on top of strict tool schemas.
3. Treat persona style as a research variable only with an explicit protocol: voice must not change evidence access, budgets or evaluator inputs, and any LLM output must be checked for unsupported facts/citations.
