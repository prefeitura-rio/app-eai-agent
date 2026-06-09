# -*- coding: utf-8 -*-
"""
Evaluator de tokens FATURADOS reais (billing footprint), distinto do
``token_usage_total`` (que estima chars/4 do transcript visível — proxy de
tamanho-de-memória, NÃO o token cobrado pela API).

Lê o ``usage_statistics`` que o engine já emite (``prompt_tokens`` =
``prompt_token_count`` do Vertex, somado por turno em
``message_formatter.calculate_usage_statistics``) — o INPUT realmente cobrado,
incluindo system prompt + tools + memória re-submetida, que o chars/4 não enxerga.
Quando o real vier 0/ausente, cai num piso chars/4 marcado. Também expõe o split de
cache (``cached_tokens`` = ``cached_content_token_count``), que resolve a dúvida
"75% vs 90% de desconto de cache" do estudo de custos.

A lógica pura fica em ``src/utils/token_billing.py`` (sem deps pesadas, unit-testável).
Métrica INFORMATIVA (não trava o gate — ver ``comment_eval_results.py::INFORMATIONAL_METRICS``).
"""

from src.evaluations.core.eval import (
    AgentResponse,
    BaseMultipleTurnEvaluator,
    BaseOneTurnEvaluator,
    EvaluationResult,
    EvaluationTask,
    MultiTurnEvaluationInput,
)
from src.utils.token_billing import aggregate_billed
from src.utils.log import logger


class TokenUsageBilledEvaluator(BaseMultipleTurnEvaluator):
    """Tokens de input FATURADOS reais ao longo da conversa (multi-turn)."""

    name = "token_usage_billed"

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            traces = [turn.agent_reasoning_trace for turn in agent_response.transcript]
            result = aggregate_billed(traces)
            return EvaluationResult(
                score=result["score"],
                annotations=str(result["annotations"]),
                has_error=False,
                error_message=None,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Erro ao avaliar token_usage_billed (multi): {e}", exc_info=True)
            return EvaluationResult(
                score=None, annotations=None, has_error=True, error_message=str(e)
            )


class TokenUsageBilledOneTurnEvaluator(BaseOneTurnEvaluator):
    """Tokens de input FATURADOS reais de um único turno (one-turn).

    Mesmo ``name`` do multi-turn — agrega no mesmo métrico através dos experiments.
    """

    name = "token_usage_billed"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            result = aggregate_billed([agent_response.reasoning_trace])
            return EvaluationResult(
                score=result["score"],
                annotations=str(result["annotations"]),
                has_error=False,
                error_message=None,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Erro ao avaliar token_usage_billed (one): {e}", exc_info=True)
            return EvaluationResult(
                score=None, annotations=None, has_error=True, error_message=str(e)
            )
