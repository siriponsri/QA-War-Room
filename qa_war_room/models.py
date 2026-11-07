"""Credential-free model boundary. No provider SDK, network, evaluator or tools."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, DecimalException
import json
import math
import re
from typing import Protocol

from .native_data import NLI_LABELS, digest, lexical_scores


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: str = "0"

    def validate(self) -> None:
        if any(type(n) is not int or n < 0 for n in (self.input_tokens, self.output_tokens)):
            raise ValueError("Token usage must be nonnegative integers")
        try:
            cost = Decimal(self.cost_usd)
        except (DecimalException, TypeError) as error:
            raise ValueError("Cost must be a decimal string") from error
        if not cost.is_finite() or cost < 0:
            raise ValueError("Cost must be finite and nonnegative")


@dataclass(frozen=True)
class ModelResponse:
    raw: str
    usage: Usage


class ModelAdapter(Protocol):
    """An adapter receives only a serialized visible request and output cap.

    A future paid implementation needs separately authorized pricing/credentials.
    Bounds must include all internal work. There are no hidden adapter retries.
    """

    def identity(self) -> dict: ...
    def upper_bound(self, request: dict, max_output_tokens: int) -> Usage: ...
    def predict(self, request: dict, max_output_tokens: int) -> ModelResponse: ...


class OfflineAdapter:
    """A reproducible wiring fake, NOT a language model or semantic baseline."""

    def identity(self) -> dict:
        return {"provider": "offline", "model": "deterministic-wiring-v1", "temperature": 0,
                "llm": False, "token_accounting": "no_model_tokens", "retries": 0}

    def upper_bound(self, request: dict, max_output_tokens: int) -> Usage:
        return Usage()

    def predict(self, request: dict, max_output_tokens: int) -> ModelResponse:
        seed = int(digest(request), 16)
        if request["dataset"] == "drugqa":
            output = {"selected_answer": "ABCD"[seed % 4], "reasoning": "Offline wiring fake; no regulatory reasoning."}
        else:
            content = json.loads(request["messages"][1]["content"])
            spans = content["spans"]
            scores = lexical_scores(content["hypothesis"], [s["text"] for s in spans])
            output = {"label": NLI_LABELS[seed % 3],
                      "evidence_span_ids": [s["id"] for s, score in zip(spans, scores) if score > 0.5],
                      "span_scores": {str(s["id"]): score for s, score in zip(spans, scores)}}
        return ModelResponse(json.dumps(output, ensure_ascii=False), Usage())


def validate_prediction(raw: str, request: dict) -> dict:
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > 1_000_000:
        raise ValueError("Output must be bounded text")
    if request["dataset"] == "drugqa":
        # Match the pinned reference client's quoted-field priority and word fallback.
        for field in ("selected_answer", "predicted_answer"):
            match = re.search(r'"' + field + r'"\s*:\s*"([ABCD])"', raw, re.I)
            if match:
                return {"answer": match[1].upper()}
        match = re.search(r"\b([ABCD])\b", raw.upper())
        if match:
            return {"answer": match[1]}
        raise ValueError("Unmapped native MCQ answer")
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("Duplicate JSON object key")
            obj[key] = value
        return obj
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or set(value) != {"label", "evidence_span_ids", "span_scores"}:
        raise ValueError("Unexpected native prediction fields")
    if value["label"] not in NLI_LABELS:
        raise ValueError("Invalid native NLI label")
    ids, scores = value["evidence_span_ids"], value["span_scores"]
    visible = set(request["visible_span_ids"])
    if (not isinstance(ids, list) or any(type(i) is not int for i in ids) or
            len(set(ids)) != len(ids) or not set(ids) <= visible):
        raise ValueError("Citations must be unique visible span IDs")
    if not isinstance(scores, dict) or set(scores) != {str(i) for i in visible}:
        raise ValueError("Every visible span needs exactly one score")
    if any(type(n) not in (int, float) or not math.isfinite(n) or not 0 <= n <= 1 for n in scores.values()):
        raise ValueError("Span scores must be finite numbers between zero and one")
    return value
