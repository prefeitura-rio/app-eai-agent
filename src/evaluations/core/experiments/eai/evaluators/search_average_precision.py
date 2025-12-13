# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class SearchAveragePrecisionEvaluator(BaseOneTurnEvaluator):
    """
    Avalia o Average Precision (AP) dos documentos retornados pelo google_search
    comparando com uma lista de documentos esperados (golden_documents_list).
    
    AP considera a ordem dos documentos retornados:
    - Para cada posição k onde um documento relevante aparece, calcula Precision@k
    - AP = (soma de todas as Precision@k para docs relevantes) / (total de docs golden)
    
    Retorna None se:
    - google_search não foi chamado
    - O formato retornado não é Typesense (response com lista de docs com title e id)
    - golden_documents_list está vazio ou é None
    
    Se há múltiplas chamadas ao google_search, retorna o AP máximo.
    """

    name = "search_average_precision"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            # Verifica se golden_documents_list existe e não está vazio
            golden_docs = self._parse_golden_documents(task.golden_documents_list)
            if not golden_docs:
                return EvaluationResult(
                    score=None,
                    annotations="No golden documents provided",
                    has_error=False,
                    error_message=None,
                )

            # Extrai todas as chamadas válidas do google_search
            search_calls = self._extract_google_search_calls(agent_response)
            
            if not search_calls:
                return EvaluationResult(
                    score=None,
                    annotations="No valid google_search calls with Typesense format found",
                    has_error=False,
                    error_message=None,
                )

            # Calcula o AP para cada chamada e pega o máximo
            aps = []
            ap_details = []
            
            for call_idx, returned_ids in enumerate(search_calls):
                ap, details = self._calculate_average_precision(returned_ids, golden_docs)
                aps.append(ap)
                ap_details.append({
                    "call_index": call_idx,
                    "returned_ids": returned_ids,
                    "average_precision": ap,
                    "precision_at_k_details": details,
                })

            max_ap = max(aps)
            max_ap_idx = aps.index(max_ap)

            return EvaluationResult(
                score=max_ap,
                annotations={
                    "golden_documents": golden_docs,
                    "max_average_precision": max_ap,
                    "max_ap_call_index": max_ap_idx,
                    "all_average_precisions": aps,
                    "ap_details": ap_details,
                    "total_google_search_calls": len(search_calls),
                },
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

    def _calculate_average_precision(self, returned_ids: list[str], golden_docs: list[str]) -> tuple[float, list[dict]]:
        """
        Calcula o Average Precision para uma lista de documentos retornados.
        
        Args:
            returned_ids: Lista de IDs dos documentos retornados (em ordem)
            golden_docs: Lista de IDs dos documentos relevantes (golden)
            
        Returns:
            tuple: (average_precision, details_list)
                - average_precision: O valor do AP
                - details_list: Lista com detalhes de cada posição relevante
        """
        if not returned_ids or not golden_docs:
            return 0.0, []
        
        golden_set = set(golden_docs)
        num_relevant_found = 0
        sum_precisions = 0.0
        details = []
        
        # Itera por cada posição k (1-indexed para cálculo de precisão)
        for k, doc_id in enumerate(returned_ids, start=1):
            is_relevant = doc_id in golden_set
            
            if is_relevant:
                num_relevant_found += 1
                precision_at_k = num_relevant_found / k
                sum_precisions += precision_at_k
                
                details.append({
                    "position": k,
                    "doc_id": doc_id,
                    "is_relevant": True,
                    "precision_at_k": precision_at_k,
                    "relevant_found_so_far": num_relevant_found,
                })
            else:
                details.append({
                    "position": k,
                    "doc_id": doc_id,
                    "is_relevant": False,
                    "precision_at_k": None,
                })
        
        # AP = soma das precisões nos pontos relevantes / total de documentos relevantes
        average_precision = sum_precisions / len(golden_docs) if golden_docs else 0.0
        
        return average_precision, details

    def _parse_golden_documents(self, golden_documents_list) -> list[str]:
        """
        Parse a lista de documentos esperados.
        Retorna uma lista vazia se não houver documentos válidos.
        """
        if not golden_documents_list:
            return []
        
        # Se é uma string, tenta fazer parse
        if isinstance(golden_documents_list, str):
            golden_documents_list = golden_documents_list.strip()
            if not golden_documents_list:
                return []
            
            # Remove colchetes externos se existirem (caso seja string de lista)
            if golden_documents_list.startswith('[') and golden_documents_list.endswith(']'):
                golden_documents_list = golden_documents_list[1:-1].strip()
            
            # Remove aspas externas se existirem
            if golden_documents_list.startswith("'") and golden_documents_list.endswith("'"):
                golden_documents_list = golden_documents_list[1:-1].strip()
            elif golden_documents_list.startswith('"') and golden_documents_list.endswith('"'):
                golden_documents_list = golden_documents_list[1:-1].strip()
            
            # Tenta separar por vírgula, ponto-e-vírgula ou espaço
            if ',' in golden_documents_list:
                docs = [doc.strip().strip("'").strip('"') for doc in golden_documents_list.split(',')]
            elif ';' in golden_documents_list:
                docs = [doc.strip().strip("'").strip('"') for doc in golden_documents_list.split(';')]
            else:
                docs = [doc.strip().strip("'").strip('"') for doc in golden_documents_list.split()]
            
            return [doc for doc in docs if doc]
        
        # Se já é uma lista, retorna
        if isinstance(golden_documents_list, list):
            return [str(doc).strip().strip("'").strip('"') for doc in golden_documents_list if doc]
        
        return []

    def _extract_google_search_calls(self, agent_response: AgentResponse) -> list[list[str]]:
        """
        Extrai os IDs dos documentos retornados por cada chamada do google_search
        que tenha o formato Typesense válido.
        
        Retorna uma lista de listas, onde cada lista interna contém os IDs
        dos documentos retornados por uma chamada específica (na ordem retornada).
        """
        search_calls = []

        if not agent_response or not agent_response.reasoning_trace:
            return search_calls
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if step.content.get("name") != "google_search":
                continue

            tool_return = step.content.get("tool_return", {})
            
            # Verifica se tem formato Typesense válido
            if not self._is_valid_typesense_format(tool_return):
                continue
            
            # Extrai os IDs dos documentos (mantém a ordem)
            response = tool_return.get("response", [])
            doc_ids = [doc.get("id") for doc in response if doc.get("id")]
            
            if doc_ids:
                search_calls.append(doc_ids)
        
        return search_calls

    def _is_valid_typesense_format(self, tool_return: dict) -> bool:
        """
        Verifica se o tool_return tem o formato Typesense válido:
        - Tem chave 'response' com uma lista
        - Cada item da lista tem pelo menos 'title' e 'id'
        """
        if "response" not in tool_return:
            return False
        
        response = tool_return.get("response")
        if not isinstance(response, list):
            return False
        
        if len(response) == 0:
            return False
        
        # Verifica se todos os itens têm 'title' e 'id'
        return all(
            isinstance(item, dict) and "title" in item and "id" in item
            for item in response
        )
