# -*- coding: utf-8 -*-
"""
Testes da lógica pura do ``token_usage_billed`` (footprint de tokens FATURADOS).

Importa SÓ o módulo core (sem deps pesadas de config/bigquery/GCP), então roda
sem o env de infra.
"""

from src.utils.token_billing import (
    aggregate_billed,
    estimate_floor_tokens,
    find_usage_statistics,
)


class _Step:
    """Stub mínimo de ReasoningStep (message_type + content)."""

    def __init__(self, message_type, content):
        self.message_type = message_type
        self.content = content


def _usage_step(prompt, cached=0, completion=0, total=None):
    return _Step(
        "usage_statistics",
        {
            "prompt_tokens": prompt,
            "cached_tokens": cached,
            "completion_tokens": completion,
            "total_tokens": total if total is not None else prompt + completion,
        },
    )


def test_uses_real_billed_prompt_tokens_when_present():
    """Com usage_statistics real, usa o prompt_tokens FATURADO, não chars/4."""
    trace = [
        _Step("reasoning_message", "um texto curto de raciocínio"),
        _usage_step(prompt=36000, cached=9000, completion=200),
    ]
    out = aggregate_billed([trace])
    a = out["annotations"]
    assert out["score"] == 36000  # real, não o ~7 do chars/4 do texto
    assert a["real_prompt_tokens"] == 36000
    assert a["cached_tokens"] == 9000
    assert a["uncached_prompt_tokens"] == 27000
    assert a["cache_hit_ratio"] == 0.25  # 9000/36000
    assert a["real_turns"] == 1 and a["estimated_turns"] == 0
    assert a["coverage"] == 1.0


def test_falls_back_to_floor_when_usage_missing_or_zero():
    """Sem usage real (ou prompt_tokens=0), cai no piso chars/4, marcado."""
    text = "x" * 400  # 400 chars → ~100 tok no piso
    trace_missing = [_Step("reasoning_message", text)]
    trace_zero = [_Step("reasoning_message", text), _usage_step(prompt=0)]
    out = aggregate_billed([trace_missing, trace_zero])
    a = out["annotations"]
    assert a["real_prompt_tokens"] == 0
    assert a["estimated_floor_prompt_tokens"] == 200  # 2 × ~100
    assert a["estimated_turns"] == 2 and a["real_turns"] == 0
    assert a["coverage"] == 0.0
    assert a["cache_hit_ratio"] is None
    assert all(t["method"] == "estimated_floor" for t in a["breakdown_by_turn"])


def test_mixed_turns_sum_real_plus_floor_with_coverage():
    """Conversa com turno real + turno sem usage: soma real + piso, coverage 0.5."""
    real = [_usage_step(prompt=30000, cached=6000)]
    miss = [_Step("tool_call_message", "y" * 800)]  # ~200 no piso
    out = aggregate_billed([real, miss])
    a = out["annotations"]
    assert a["real_prompt_tokens"] == 30000
    assert a["estimated_floor_prompt_tokens"] == 200
    assert out["score"] == 30200
    assert a["cached_tokens"] == 6000
    assert a["coverage"] == 0.5


def test_estimate_floor_tokens_rule():
    assert estimate_floor_tokens("") == 0
    assert estimate_floor_tokens("abcd") == 1  # 4 chars / 4
    assert estimate_floor_tokens("a" * 400) == 100


def test_find_usage_statistics_picks_the_right_step():
    trace = [_Step("reasoning_message", "nada"), _usage_step(prompt=123)]
    found = find_usage_statistics(trace)
    assert found is not None and found["prompt_tokens"] == 123
    assert find_usage_statistics([]) is None
    assert find_usage_statistics(None) is None
