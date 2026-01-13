# -*- coding: utf-8 -*-
"""
TypesenseActivateEvaluator - Binary metric to check if Typesense was activated as search source.

Scenarios:
    1. Should activate + Did NOT activate -> Score 0
    2. Should activate + Did activate     -> Score 1
    3. Should NOT activate + Did NOT activate -> Score None
    4. Should NOT activate + Did activate     -> Score None

"Should activate" is determined by: golden_documents_list is defined and not empty
"Did activate" is determined by: search results have Typesense format (id, title, score_info)
"""

from typing import List, Dict, Any, Optional

from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
)
from src.evaluations.core.experiments.eai.evaluators.typesense.base import (
    BaseTypesenseEvaluator,
)


class TypesenseActivateEvaluator(BaseTypesenseEvaluator):
    """
    Binary evaluator that checks if Typesense was activated as the search source.
    
    Typesense results are identified by having documents with fields: id, title, and score_info.
    """

    name = "typesense_activate"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            # Determine if Typesense SHOULD have been activated
            golden_docs = self.parse_golden_documents(
                getattr(task, 'golden_documents_list', None)
            )
            should_activate = len(golden_docs) > 0
            
            # Determine if Typesense WAS activated
            did_activate = self._check_typesense_activated(agent_response)
            
            # Apply scenario logic
            score, annotation = self._evaluate_scenario(
                should_activate=should_activate,
                did_activate=did_activate,
                agent_response=agent_response,
            )

            return EvaluationResult(
                score=score,
                annotations=annotation,
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

    def _check_typesense_activated(self, agent_response: AgentResponse) -> bool:
        """
        Check if any search result has Typesense format (id, title, score_info).
        """
        if not agent_response or not agent_response.reasoning_trace:
            return False
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if not isinstance(step.content, dict):
                continue
            
            tool_name = step.content.get("name", "")
            if tool_name not in ["google_search", "dharma_search_tool"]:
                continue
                
            tool_return = step.content.get("tool_return", {})
            if not isinstance(tool_return, dict):
                continue
            
            documents = tool_return.get("response") or tool_return.get("documents", [])
            if not isinstance(documents, list) or len(documents) == 0:
                continue
            
            # Check if documents have Typesense format
            if self._is_typesense_format(documents):
                return True
        
        return False

    def _is_typesense_format(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Check if documents are in Typesense format.
        Typesense format requires: id, title, and score_info fields.
        """
        if not documents:
            return False
        
        return all(
            isinstance(doc, dict) 
            and "id" in doc 
            and "title" in doc 
            and "score_info" in doc
            for doc in documents
        )

    def _evaluate_scenario(
        self,
        should_activate: bool,
        did_activate: bool,
        agent_response: AgentResponse,
    ) -> tuple:
        """
        Evaluate based on the 4 scenarios:
        
        1. Should activate + Did NOT activate -> Score 0
        2. Should activate + Did activate     -> Score 1
        3. Should NOT activate + Did NOT activate -> Score None
        4. Should NOT activate + Did activate     -> Score None
        
        Returns:
            tuple: (score, annotation)
        """
        # Get search details for annotation
        search_executed = self.has_search_been_executed(agent_response)
        search_details = self._get_search_details(agent_response)
        
        if should_activate:
            if did_activate:
                # Scenario 2: Should activate + Did activate -> Score 1
                annotation = self._build_annotation(status="Typesense ativado")
                return (1, annotation)
            else:
                # Scenario 1: Should activate + Did NOT activate -> Score 0
                reason = "Nenhuma busca executada" if not search_executed else "Busca não retornou formato Typesense"
                annotation = self._build_annotation(
                    status="Typesense NÃO ativado",
                    reason=reason,
                )
                return (0, annotation)
        else:
            # Scenarios 3 and 4: Should NOT activate -> Score None
            if did_activate:
                annotation = self._build_annotation(status="Typesense ativado (não esperado)")
            else:
                annotation = self._build_annotation(status="Typesense não ativado (não esperado)")
            return (None, annotation)

    def _get_search_details(self, agent_response: AgentResponse) -> List[Dict[str, Any]]:
        """Get details about each search call for the annotation."""
        details = []
        
        if not agent_response or not agent_response.reasoning_trace:
            return details
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if not isinstance(step.content, dict):
                continue
            
            tool_name = step.content.get("name", "")
            if tool_name not in ["google_search", "dharma_search_tool"]:
                continue
                
            tool_return = step.content.get("tool_return", {})
            if not isinstance(tool_return, dict):
                continue
            
            documents = tool_return.get("response") or tool_return.get("documents", [])
            if not isinstance(documents, list):
                continue
            
            is_typesense = self._is_typesense_format(documents) if documents else False
            sample_fields = list(documents[0].keys())[:5] if documents and isinstance(documents[0], dict) else []
            
            details.append({
                "doc_count": len(documents),
                "is_typesense": is_typesense,
                "sample_fields": sample_fields,
            })
        
        return details

    def _build_annotation(
        self,
        status: str,
        reason: Optional[str] = None,
    ) -> str:
        """Build markdown annotation - only status and reason."""
        lines = []
        
        lines.append(f"**Status:** {status}")
        
        if reason:
            lines.append(f"**Motivo:** {reason}")
        
        return "\n".join(lines)
