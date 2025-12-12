# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class TypesenseFormatEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do google_search retorna o formato correto do Typesense.
    Verifica se tool_return contém uma chave 'response' com uma lista onde cada
    item possui pelo menos 'title' e 'id'.
    """

    name = "activate_typesense"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            has_correct_format = self._check_typesense_format(agent_response)
            score = 1 if has_correct_format else 0
            
            if has_correct_format:
                annotations = "At least one google_search call returned the correct Typesense format"
            else:
                annotations = "No google_search calls with correct Typesense format found"
            
            return EvaluationResult(
                score=score,
                annotations=annotations,
                has_error=False,
                error_message=None,
            )

        except Exception as e:
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )

    def _check_typesense_format(self, agent_response: AgentResponse) -> bool:
        """
        Verifica se alguma chamada do google_search retornou o formato correto.
        Retorna True se pelo menos uma chamada tiver o formato correto.
        """
        if not agent_response or not agent_response.reasoning_trace:
            return False
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if step.content.get("name") != "google_search":
                continue

            tool_return = step.content.get("tool_return", {})
            
            # Verifica se tem a chave 'response' com uma lista
            if "response" not in tool_return:
                continue
            
            response = tool_return.get("response")
            if not isinstance(response, list):
                continue
            
            # Verifica se a lista não está vazia e se cada item tem 'title' e 'id'
            if len(response) == 0:
                continue
            
            # Verifica se todos os itens da lista têm 'title' e 'id'
            all_valid = all(
                isinstance(item, dict) and "title" in item and "id" in item
                for item in response
            )
            
            if all_valid:
                return True
        
        return False
