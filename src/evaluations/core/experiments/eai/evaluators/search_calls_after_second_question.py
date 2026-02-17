# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)
from src.utils.log import logger


class SearchCallsAfterSecondQuestionEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia quantas chamadas à ferramenta google_search foram realizadas
    após o recebimento da segunda pergunta do usuário.
    
    Valores esperados:
    - 0: Reutilizou memória corretamente (ideal)
    - 1: Precisou buscar novamente
    - >1: Instabilidade ou loop de buscas
    """

    name = "search_calls_after_second_question"

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Conta quantas chamadas de google_search ocorreram após a segunda pergunta.
        """
        try:
            transcript = agent_response.transcript
            task_dict = task.model_dump(exclude_none=True)
            secondary_message = task_dict.get('secondary_user_message', '')
            
            # Verifica se há mensagem secundária configurada
            if not secondary_message:
                return EvaluationResult(
                    score=None,
                    annotations="secondary_user_message não definida na task",
                    has_error=True,
                    error_message="secondary_user_message não encontrada"
                )
            
            # Identifica qual turno contém a secondary_user_message
            secondary_turn_index = None
            for idx, turn in enumerate(transcript):
                if turn.user_message and secondary_message.lower() in turn.user_message.lower():
                    secondary_turn_index = idx
                    break
            
            # Se não encontrou a segunda pergunta, retorna erro
            if secondary_turn_index is None:
                return EvaluationResult(
                    score=None,
                    annotations=f"secondary_user_message ('{secondary_message}') não encontrada na conversa",
                    has_error=True,
                    error_message="Segunda pergunta não foi feita na conversa"
                )
            
            # Conta chamadas de google_search APÓS o turno da segunda pergunta
            # Precisamos olhar a resposta do agente à segunda pergunta
            search_calls_count = 0
            turns_analyzed = 0
            
            # Analisa apenas os turnos APÓS a secondary_user_message
            for turn in transcript[secondary_turn_index:]:
                turns_analyzed += 1
                if turn.agent_reasoning_trace:
                    for step in turn.agent_reasoning_trace:
                        # Verifica se é uma tool_call do tipo google_search
                        if step.message_type == "tool_call_message":
                            # O content é um dict com name e arguments
                            if isinstance(step.content, dict):
                                tool_name = step.content.get("name", "")
                                if "google_search" in tool_name.lower():
                                    search_calls_count += 1
            
            # Interpretação do resultado
            if search_calls_count == 0:
                interpretation = "Reutilizou memória corretamente - nenhuma busca adicional"
            elif search_calls_count == 1:
                interpretation = "Precisou buscar novamente"
            else:
                interpretation = f"Instabilidade detectada - {search_calls_count} buscas realizadas"
            
            annotations = {
                "interpretation": interpretation,
                "search_calls_count": search_calls_count,
                "secondary_turn_index": secondary_turn_index + 1,  # 1-based
                "turns_analyzed_after_secondary": turns_analyzed,
            }
            
            return EvaluationResult(
                score=search_calls_count,
                annotations=str(annotations),
                has_error=False,
                error_message=None,
            )

        except Exception as e:
            logger.error(
                f"Erro ao avaliar search_calls_after_second_question: {e}",
                exc_info=True,
            )
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )
