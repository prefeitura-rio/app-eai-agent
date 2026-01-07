# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class SearchRecallEvaluator(BaseOneTurnEvaluator):
    """
    Avalia o recall dos documentos retornados pelo google_search comparando
    com uma lista de documentos esperados (golden_documents_list).
    
    Recall = (número de documentos golden retornados) / (total de documentos golden)
    
    Retorna None se:
    - google_search não foi chamado
    - O formato retornado não é Typesense (response com lista de docs com title e id)
    - golden_documents_list está vazio ou é None
    
    Se há múltiplas chamadas ao google_search, retorna o recall máximo.
    """

    name = "search_recall"

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

            # Calcula o recall para cada chamada e pega o máximo
            recalls = []
            recall_details = []
            
            for call_idx, returned_ids in enumerate(search_calls):
                matches = [doc_id for doc_id in golden_docs if doc_id in returned_ids]
                recall = len(matches) / len(golden_docs)
                
                recalls.append(recall)
                recall_details.append({
                    "call_index": call_idx,
                    "returned_ids": returned_ids,
                    "matched_ids": matches,
                    "recall": recall,
                    "total_golden": len(golden_docs),
                    "total_matches": len(matches),
                })

            max_recall = max(recalls)
            max_recall_idx = recalls.index(max_recall)

            return EvaluationResult(
                score=max_recall,
                annotations={
                    "golden_documents": golden_docs,
                    "max_recall": max_recall,
                    "max_recall_call_index": max_recall_idx,
                    "all_recalls": recalls,
                    "recall_details": recall_details,
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
        ou dharma_search_tool que tenha o formato Typesense válido.
        
        Retorna uma lista de listas, onde cada lista interna contém os IDs
        dos documentos retornados por uma chamada específica (na ordem retornada).
        """
        search_calls = []

        if not agent_response or not agent_response.reasoning_trace:
            return search_calls
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            # if step.content.get("name") != "google_search":
            #     continue

            tool_return = step.content.get("tool_return", {})
            
            # Verifica se tem formato Typesense válido
            if not self._is_valid_typesense_format(tool_return):
                continue
            
            # Extrai os IDs dos documentos (mantém a ordem)
            # Suporta tanto 'response' (google_search) quanto 'documents' (dharma_search_tool)
            docs_list = tool_return.get("response") or tool_return.get("documents", [])
            doc_ids = [doc.get("id") for doc in docs_list if doc.get("id")]
            
            if doc_ids:
                search_calls.append(doc_ids)
        
        return search_calls

    def _is_valid_typesense_format(self, tool_return: dict) -> bool:
        """
        Verifica se o tool_return tem o formato Typesense válido:
        - Tem chave 'response' (google_search) ou 'documents' (dharma_search_tool) com uma lista
        - Cada item da lista tem pelo menos 'title' e 'id'
        """
        # Suporta tanto 'response' quanto 'documents'
        docs_list = tool_return.get("response") or tool_return.get("documents")
        
        if not docs_list:
            return False
        
        if not isinstance(docs_list, list):
            return False
        
        if len(docs_list) == 0:
            return False
        
        # Verifica se todos os itens têm 'title' e 'id'
        return all(
            isinstance(item, dict) and "title" in item and "id" in item
            for item in docs_list
        )
