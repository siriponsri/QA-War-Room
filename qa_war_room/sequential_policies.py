"""Offline wiring policies; observation in, one strict action out. No file I/O."""

from .native_data import NLI_LABELS, digest, lexical_scores

POLICIES = ("catalog-wiring-v1", "random-wiring-v1", "catalog-guarded-wiring-v1")


def choose_action(observation: dict, policy: str, seed: int = 0) -> dict:
    if policy not in POLICIES or observation["status"] != "active":
        raise ValueError("Choose an offline policy for an active observation")
    remaining = [row for row in observation["catalog"] if not row["requested"]]
    if remaining and observation["budget"]["credits_remaining"] > 0:
        if policy == "random-wiring-v1":
            remaining.sort(key=lambda row: digest([seed, observation["episode_id"], row["id"]]))
        return {"type": "request", "record_id": remaining[0]["id"]}
    label = NLI_LABELS[int(digest(observation), 16) % len(NLI_LABELS)]
    full_source = len(observation["evidence"]) == len(observation["catalog"])
    if not observation["evidence"] or (policy == "catalog-guarded-wiring-v1" and not full_source):
        return {"type": "abstain", "forced_label": label,
                "reason": "Offline wiring policy: no evidence or full-source exposure guard not met. No semantic inference."}
    spans = [span for record in observation["evidence"] for span in record["spans"]]
    # Only acquired text may be ranked. The ranking cannot select hidden records.
    scores = lexical_scores(observation["hypothesis"], [span["text"] for span in spans])
    citations = [spans[i]["id"] for i in sorted(range(len(spans)), key=lambda i: (-scores[i], spans[i]["id"]))[:3]]
    return {"type": "submit", "label": label, "citation_span_ids": citations,
            "rationale": "Hash-selected offline wiring label with visible-only lexical citations; not semantic reasoning."}
