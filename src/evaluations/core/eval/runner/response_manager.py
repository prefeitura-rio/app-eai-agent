# -*- coding: utf-8 -*-
import time
from typing import Optional, Dict, Any, Tuple, AsyncGenerator
from contextlib import asynccontextmanager

from src.evaluations.core.eval.llm_clients import EAIConversationManager
from src.evaluations.core.eval.schemas import (
    AgentResponse,
    ReasoningStep,
    EvaluationTask,
    ConversationOutput,
    ConversationTurn,
)
from src.evaluations.core.eval.evaluators.base import BaseConversationEvaluator
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.eval.log import logger
from src.services.eai_gateway.api import EAIClient


class ResponseManager:
    """
    Abstrai a obtenção de respostas do agente, seja de uma execução ao vivo
    ou de um cache pré-computado.
    """

    def __init__(
        self,
        agent_config: Dict[str, Any],
        precomputed_responses: Optional[Dict[str, Dict[str, Any]]] = None,
        eai_client: EAIClient = EAIClient(),
    ):
        self.agent_config = agent_config
        self.precomputed_responses = precomputed_responses or {}
        self.eai_client = eai_client

    @asynccontextmanager
    async def _get_agent_manager(
        self,
    ) -> AsyncGenerator[Optional[EAIConversationManager], None]:
        """Context manager para gerenciar o ciclo de vida do agente."""
        if self.precomputed_responses:
            yield None
            return

        agent_manager = EAIConversationManager(
            agent_config=CreateAgentRequest(**self.agent_config),
            eai_client=self.eai_client,
        )
        try:
            await agent_manager.initialize()
            yield agent_manager
        finally:
            await agent_manager.close()

    async def get_one_turn_response(
        self, task: EvaluationTask
    ) -> Tuple[AgentResponse, float]:
        """Obtém resposta de turno único, usando cache se disponível."""
        task_id = task.id
        if self.precomputed_responses:
            precomputed = self.precomputed_responses.get(task_id, {})
            if "one_turn_output" in precomputed:
                logger.debug(f"↪️ Usando one-turn pré-computado para {task_id}")
                response = AgentResponse(
                    output=precomputed["one_turn_output"],
                    messages=[
                        ReasoningStep(
                            message_type="precomputed",
                            content=precomputed["one_turn_output"],
                        )
                    ],
                )
                return response, 0.0
            else:
                logger.warning(
                    f"❌ Dados one-turn não encontrados para {task_id} em precomputed_responses"
                )
                return AgentResponse(output=None, messages=[]), 0.0

        logger.debug(f"▶️ Gerando one-turn ao vivo para {task_id}")
        start_time = time.perf_counter()
        async with self._get_agent_manager() as agent_manager:
            if not agent_manager:
                # Isso só deve acontecer se estivermos usando respostas pré-computadas,
                # o que já foi tratado. Lançar um erro aqui é uma salvaguarda.
                raise RuntimeError(
                    "Falha ao obter o gerenciador de agente, mesmo não usando respostas pré-computadas."
                )
            response = await agent_manager.send_message(task.prompt)
            return response, time.perf_counter() - start_time

    async def get_multi_turn_transcript(
        self, task: EvaluationTask, conv_evaluator: BaseConversationEvaluator
    ) -> Optional[ConversationOutput]:
        """Obtém transcrição multi-turn, usando cache se disponível."""
        task_id = task.id
        if self.precomputed_responses:
            precomputed = self.precomputed_responses.get(task_id, {})
            if "multi_turn_transcript" in precomputed:
                logger.debug(f"↪️ Usando multi-turn pré-computado para {task_id}")
                try:
                    transcript_data = precomputed["multi_turn_transcript"]
                    transcript = [ConversationTurn(**turn) for turn in transcript_data]
                    history = [
                        f"Turno {t.turn} - User: {t.judge_message}\n"
                        f"Turno {t.turn} - Agente: {t.agent_response}"
                        for t in transcript
                        if t.agent_response
                    ]
                    final_response = transcript[-1] if transcript else None
                    final_agent_response = AgentResponse(
                        output=(
                            final_response.agent_response if final_response else None
                        ),
                        messages=(
                            final_response.reasoning_trace if final_response else []
                        ),
                    )
                    return ConversationOutput(
                        transcript=transcript,
                        final_agent_response=final_agent_response,
                        history_for_judge=history,
                        duration_seconds=0.0,
                    )
                except Exception as e:
                    logger.error(
                        f"Erro ao processar transcript pré-computado para {task_id}: {e}"
                    )
                    # Retorna None para indicar falha no processamento do cache
                    return None
            else:
                logger.warning(
                    f"❌ Dados multi-turn não encontrados para {task_id} em precomputed_responses"
                )
                return None

        logger.debug(f"▶️ Gerando multi-turn ao vivo para {task_id}")
        async with self._get_agent_manager() as agent_manager:
            if not agent_manager:
                raise RuntimeError("Falha ao inicializar o agente para multi-turn.")
            return await conv_evaluator.evaluate(task, agent_manager)
