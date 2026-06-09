# -*- coding: utf-8 -*-
"""
Lógica PURA do ``token_usage_billed`` — SEM imports pesados (config/bigquery/GCP),
pra ser unit-testável sem o env de infra. As classes Evaluator (que importam as
base classes pesadas) vivem em ``token_usage_billed.py`` e chamam ``aggregate_billed``.

``token_usage_billed`` lê o token de INPUT realmente FATURADO (``prompt_tokens`` do
``usage_statistics``, = ``prompt_token_count`` do Vertex, incluindo system prompt +
tools + memória re-submetida) — distinto do ``token_usage_total``, que estima chars/4
só do transcript visível. Quando o real vier 0/ausente num turno, usa um piso chars/4
marcado. Também agrega o split de cache (``cached_tokens``).
"""

from typing import Any, Dict, List, Optional


def estimate_floor_tokens(text: str) -> int:
    """Piso chars/4 (mesma regra do ``token_usage_total.estimate_tokens_from_text``)."""
    if not text:
        return 0
    return int(len(text.strip()) / 4)


def find_usage_statistics(reasoning_trace: Optional[List[Any]]) -> Optional[Dict[str, Any]]:
    """Acha o step ``usage_statistics`` num reasoning_trace e devolve seu content (dict)."""
    if not reasoning_trace:
        return None
    for step in reasoning_trace:
        if getattr(step, "message_type", None) == "usage_statistics":
            content = getattr(step, "content", None)
            if isinstance(content, dict):
                return content
    return None


def estimate_floor_from_trace(reasoning_trace: Optional[List[Any]]) -> int:
    """Piso chars/4 do texto visível do trace — usado SÓ quando o real não vem.

    É um piso (subconta): não enxerga system prompt/tools/memória, que dominam o
    input faturado. Serve pra o score não zerar em turnos sem usage real.
    """
    if not reasoning_trace:
        return 0
    total = 0
    for step in reasoning_trace:
        if getattr(step, "message_type", None) == "usage_statistics":
            continue
        content = getattr(step, "content", None)
        if content:
            total += estimate_floor_tokens(str(content))
    return total


def aggregate_billed(reasoning_traces: List[Optional[List[Any]]]) -> Dict[str, Any]:
    """Agrega o token faturado real (com piso chars/4 onde faltar) sobre N turnos.

    ``reasoning_traces`` = um trace por turno (one-turn → lista de 1). Devolve
    ``{"score": <billed_prompt_tokens>, "annotations": {...}}``.
    """
    real_prompt = 0
    estimated_prompt = 0
    cached = 0
    completion = 0
    real_turns = 0
    estimated_turns = 0
    per_turn: List[Dict[str, Any]] = []

    for idx, trace in enumerate(reasoning_traces):
        usage = find_usage_statistics(trace)
        prompt_real = int((usage or {}).get("prompt_tokens") or 0)

        if prompt_real > 0:
            cached_turn = int((usage or {}).get("cached_tokens") or 0)
            real_prompt += prompt_real
            completion += int((usage or {}).get("completion_tokens") or 0)
            cached += cached_turn
            real_turns += 1
            per_turn.append(
                {
                    "turn": idx + 1,
                    "method": "real",
                    "prompt_tokens": prompt_real,
                    "cached_tokens": cached_turn,
                }
            )
        else:
            floor = estimate_floor_from_trace(trace)
            estimated_prompt += floor
            estimated_turns += 1
            per_turn.append(
                {"turn": idx + 1, "method": "estimated_floor", "prompt_tokens": floor}
            )

    total_billed_prompt = real_prompt + estimated_prompt
    uncached_prompt = max(real_prompt - cached, 0)
    n_turns = len(reasoning_traces) or 1

    annotations = {
        "metric": "token_usage_billed",
        "billed_prompt_tokens": total_billed_prompt,
        "real_prompt_tokens": real_prompt,
        "estimated_floor_prompt_tokens": estimated_prompt,
        "completion_tokens": completion,
        "cached_tokens": cached,
        "uncached_prompt_tokens": uncached_prompt,
        "cache_hit_ratio": round(cached / real_prompt, 4) if real_prompt else None,
        "real_turns": real_turns,
        "estimated_turns": estimated_turns,
        "coverage": round(real_turns / n_turns, 4),
        "breakdown_by_turn": per_turn,
        "note": (
            "score = prompt_tokens faturado real (usage_statistics) somado; "
            "turnos sem usage real usam piso chars/4 (subconta). cached_tokens = "
            "parcela servida do cache implícito do Vertex."
        ),
    }
    return {"score": total_billed_prompt, "annotations": annotations}
