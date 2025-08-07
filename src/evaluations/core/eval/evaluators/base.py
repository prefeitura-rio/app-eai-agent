# -*- coding: utf-8 -*-
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Union, List

from src.evaluations.core.eval.llm_clients import (
    BaseJudgeClient,
    EAIConversationManager,
)
from src.evaluations.core.eval.schemas import (
    EvaluationTask,
    EvaluationResult,
    AgentResponse,
    MultiTurnEvaluationInput,
    ConversationOutput,
    ConversationTurn,
)
from src.utils.log import logger


def _extract_evaluation_score(response: str) -> float:
    """Extrai o score de uma string formatada, retornando 0.0 se não encontrado."""
    score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
    return float(score_match.group(1)) if score_match else 0.0


class BaseEvaluator(ABC):
    """
    Classe base abstrata para todos os avaliadores de métricas.
    Define a interface que cada avaliador deve implementar, garantindo que
    cada métrica seja um componente modular e "plugável".
    """

    name: str
    turn_type: str  # 'one', 'multi', ou 'conversation'

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Ignora a validação para as próprias classes base abstratas
        if not ABC in cls.__bases__ and not "Mixin" in cls.__name__:
            if not hasattr(cls, "turn_type") or cls.turn_type not in [
                "one",
                "multi",
                "conversation",
            ]:
                raise TypeError(
                    f"Avaliador '{cls.__name__}' deve definir um 'turn_type' válido ('one', 'multi', ou 'conversation')."
                )

    def __init__(self, judge_client: BaseJudgeClient):
        """
        Inicializa o avaliador com um cliente de LLM que atuará como juiz.

        Args:
            judge_client (BaseJudgeClient): Uma instância de um cliente de LLM
                                            que adere à interface BaseJudgeClient.
        """
        self.judge_client = judge_client

    @abstractmethod
    async def evaluate(self, *args, **kwargs) -> Any:
        """
        Método principal que será implementado por todas as subclasses.
        A assinatura varia dependendo do tipo de avaliador.
        """
        raise NotImplementedError

    async def _get_llm_judgement(
        self,
        prompt_template: str,
        task: EvaluationTask,
        agent_response: Union[AgentResponse, MultiTurnEvaluationInput],
    ) -> EvaluationResult:
        """
        Formata um prompt, executa-o contra o cliente juiz e retorna um
        resultado de avaliação padronizado.

        Este método é uma implementação auxiliar para ser usada pelas subclasses.
        """
        try:
            task_dict = task.model_dump(exclude_none=True)
            response_dict = (
                agent_response
                if isinstance(agent_response, dict)
                else agent_response.model_dump(exclude_none=True)
            )

            prompt = prompt_template.format(
                task=task_dict, agent_response=response_dict
            )
            # logger.info(f"🔍 Prompt: {prompt}")
            judgement_response = await self.judge_client.execute(prompt)
            score = _extract_evaluation_score(judgement_response)
            return EvaluationResult(score=score, annotations=judgement_response)
        except Exception as e:
            logger.error(
                f"Erro durante o julgamento do LLM para o avaliador '{self.name}': {e}",
                exc_info=True,
            )
            return EvaluationResult(
                score=None,
                annotations=f"Erro na formatação ou execução do prompt: {e}",
                has_error=True,
                error_message=str(e),
            )


class BaseOneTurnEvaluator(BaseEvaluator, ABC):
    """
    Classe base para avaliadores que analisam uma única interação (one-turn).
    """

    turn_type: str = "one"

    @abstractmethod
    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Avalia uma única resposta do agente.
        """
        raise NotImplementedError


class BaseMultipleTurnEvaluator(BaseEvaluator, ABC):
    """
    Classe base para avaliadores que analisam uma conversa completa (multi-turn).
    """

    turn_type: str = "multi"

    @abstractmethod
    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Avalia uma transcrição de conversa.
        """
        raise NotImplementedError


class BaseConversationEvaluator(BaseEvaluator):
    """
    Classe base para avaliadores que GERAM uma conversa multi-turno.
    Contém a lógica de orquestração do loop da conversa, permitindo que
    classes filhas customizem o comportamento através da implementação de
    métodos específicos.
    """

    turn_type: str = "conversation"
    max_turns: int = 15
    stop_signal: str = "`EVALUATION_CONCLUDED`"

    @abstractmethod
    def get_judge_prompt(self, task: EvaluationTask, history: List[str]) -> str:
        """
        Retorna o prompt a ser enviado ao LLM-Juiz para decidir a próxima ação.
        Este método DEVE ser implementado pela classe filha.

        Args:
            task (EvaluationTask): A tarefa de avaliação atual.
            history (List[str]): O histórico da conversa formatado como uma lista de strings.

        Returns:
            str: O prompt completo para o LLM-Juiz.
        """
        raise NotImplementedError

    def is_conversation_finished(self, judge_response: str) -> bool:
        """
        Verifica se a resposta do juiz contém o sinal de parada.
        Pode ser sobrescrito para lógicas de parada mais complexas.

        Args:
            judge_response (str): A resposta do LLM-Juiz.

        Returns:
            bool: True se a conversa deve terminar, False caso contrário.
        """
        return self.stop_signal in judge_response

    async def evaluate(
        self, task: EvaluationTask, agent_manager: EAIConversationManager
    ) -> ConversationOutput:
        """
        Executa a lógica de condução da conversa.
        Este método é concreto e orquestra o diálogo usando os métodos
        `get_judge_prompt` e `is_conversation_finished` implementados/sobrescritos
        pelas classes filhas.
        """
        start_time = time.monotonic()
        transcript, history = [], []
        current_message = task.prompt or ""
        last_response = AgentResponse(message=None, reasoning_trace=[])

        for turn in range(self.max_turns):
            turn_context_string = f"multi[{turn + 1}]"
            with logger.contextualize(turn_type=turn_context_string):
                agent_res = await agent_manager.send_message(current_message)
                last_response = agent_res

                # Adiciona o turno ao transcript e ao histórico
                transcript.append(
                    ConversationTurn(
                        turn=turn + 1,
                        user_message=current_message,
                        agent_message=agent_res.message,
                        agent_reasoning_trace=agent_res.reasoning_trace,
                    )
                )
                history.append(
                    f"Turno {turn+1} - User: {current_message}\nTurno {turn+1} - Agente: {agent_res.message}"
                )

                # Usa o método da subclasse para obter o prompt do juiz
                prompt_for_judge = self.get_judge_prompt(task, history)
                judge_res = await self.judge_client.execute(prompt_for_judge)

                # Usa o método da subclasse para verificar a condição de parada
                if self.is_conversation_finished(judge_res):
                    history.append(f"Turno {turn+2} - User: {judge_res}")
                    transcript.append(
                        ConversationTurn(
                            turn=turn + 2,
                            user_message=judge_res,
                            agent_message=None,
                            agent_reasoning_trace=None,
                        )
                    )
                    break
                current_message = judge_res
        else:
            logger.warning(
                f"A conversa para a tarefa {task.id} atingiu o limite de {self.max_turns} turnos."
            )

        end_time = time.monotonic()
        duration = end_time - start_time

        return ConversationOutput(
            transcript=transcript,
            final_agent_message_details=last_response,
            conversation_history=history,
            duration_seconds=duration,
        )
