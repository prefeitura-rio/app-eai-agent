# -*- coding: utf-8 -*-
import re
from abc import ABC, abstractmethod
from typing import Any

from src.evaluations.core.eval.llm_clients import (
    BaseJudgeClient,
    EAIConversationManager,
)
from src.evaluations.core.eval.schemas import (
    EvaluationTask,
    EvaluationResult,
    ConversationOutput,
    EvaluationContext,
)
from src.utils.log import logger


def _extract_evaluation_score(response: str) -> float:
    """Extrai o score de uma string formatada, retornando 0.0 se não encontrado."""
    score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
    return float(score_match.group(1)) if score_match else 0.0


class BaseEvaluator(ABC):
    """
    Classe base abstrata para todos os avaliadores de métricas.
    Define a interface que cada avaliador deve implementar.
    """

    name: str

    def __init__(self, judge_client: BaseJudgeClient):
        self.judge_client = judge_client

    @abstractmethod
    async def evaluate(self, *args, **kwargs) -> Any:
        """Método de avaliação principal, a ser implementado pelas subclasses."""
        raise NotImplementedError


class BaseAnalysisEvaluator(BaseEvaluator):
    """
    Classe base para avaliadores que ANALISAM resultados.
    Implementa o padrão Template Method para centralizar o tratamento de erros.
    """

    required_context: str  # Deve ser 'one_turn' ou 'multi_turn'

    @abstractmethod
    async def _evaluate_logic(self, context: EvaluationContext) -> EvaluationResult:
        """
        Contém a lógica de avaliação específica do avaliador filho.
        Este método só é chamado se as verificações de pré-condição em `evaluate` passarem.
        """
        raise NotImplementedError

    async def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """
        Método Template: executa a verificação de pré-condições e, se bem-sucedido,
        delega a execução para o _evaluate_logic.
        """
        if self.required_context == "one_turn":
            response = context.one_turn_response
            if response.has_error:
                return EvaluationResult(
                    score=None,
                    annotations="Avaliação pulada devido a erro na geração da resposta de turno único.",
                    has_error=True,
                    error_message=f"Erro upstream: {response.error_message}",
                )
            if response.output is None:
                return EvaluationResult(
                    score=None,
                    annotations=f"Não foi possível avaliar '{self.name}' porque a resposta de turno único estava vazia.",
                    has_error=True,
                    error_message="Resposta de turno único com conteúdo nulo.",
                )
        elif self.required_context == "multi_turn":
            output = context.multi_turn_output
            if not output:
                return EvaluationResult(
                    score=None,
                    annotations=f"Avaliação '{self.name}' não executada porque nenhuma conversa multi-turno foi gerada.",
                    has_error=True,
                    error_message="multi_turn_output não encontrado no contexto.",
                )
            if output.has_error:
                return EvaluationResult(
                    score=None,
                    annotations="Avaliação pulada devido a erro na geração da conversa multi-turno.",
                    has_error=True,
                    error_message=f"Erro upstream: {output.error_message}",
                )
        else:
            raise ValueError(
                f"required_context inválido '{self.required_context}' no avaliador '{self.name}'"
            )

        # Se todas as verificações passaram, executa a lógica específica.
        return await self._evaluate_logic(context)

    async def _get_llm_judgement(
        self,
        prompt_template: str,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """
        Formata um prompt, executa-o contra o cliente juiz e retorna um
        resultado de avaliação padronizado.
        """
        try:
            context_dict = context.model_dump(exclude_none=True)
            prompt = prompt_template.format(context=context_dict)

            judgement_response = await self.judge_client.execute(prompt)
            score = _extract_evaluation_score(judgement_response)
            return EvaluationResult(score=score, annotations=judgement_response)
        except KeyError as e:
            error_msg = f"Erro de chave no template do prompt: a chave '{e}' não foi encontrada no contexto. Verifique se os dados necessários (one-turn ou multi-turn) estão disponíveis e se o template está correto."
            logger.error(
                f"Erro durante o julgamento do LLM para o avaliador '{self.name}': {error_msg}",
            )
            return EvaluationResult(
                score=None,
                annotations=error_msg,
                has_error=True,
                error_message=str(e),
            )
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


class BaseConversationEvaluator(BaseEvaluator):
    """
    Classe base para avaliadores que GERAM uma conversa multi-turno.
    Seu propósito não é pontuar, mas sim produzir a transcrição que
    outros avaliadores irão analisar.
    """

    @abstractmethod
    async def evaluate(
        self, task: EvaluationTask, agent_manager: EAIConversationManager
    ) -> ConversationOutput:
        """
        Executa a lógica de condução da conversa.
        """
        pass