# -*- coding: utf-8 -*-
"""
TypesenseActivateEvaluator - Binary metric to check if Typesense search was activated.

Score = 1 if search tool was called (Typesense activated), 0 otherwise
"""

from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
)
from src.evaluations.core.experiments.eai.evaluators.typesense.base import (
    BaseTypesenseEvaluator,
    TypesenseEvalContext,
)


class TypesenseActivateEvaluator(BaseTypesenseEvaluator):
    """
    Binary evaluator that checks if Typesense search was activated (search tool was called).
    
    Score = 1 if search was executed, 0 if no search was called.
    
    This evaluator shows the full annotation with all search details.
    """

    name = "typesense_activate"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            
            if not ctx.has_golden_docs:
                return EvaluationResult(
                    score=None,
                    annotations="Sem documentos esperados definidos",
                    has_error=False,
                    error_message=None,
                )
            
            search_executed = self.has_search_been_executed(agent_response)
            
            if search_executed:
                score = 1
                status = "Ativado"
            else:
                score = 0
                status = "Nao ativado (nenhuma busca executada)"
            
            annotation = self._build_full_annotation(ctx, status)
            return self.success_result(score, annotation)

        except Exception as e:
            return self.error_result(e)

    def _build_full_annotation(self, ctx: TypesenseEvalContext, status: str) -> str:
        """Build full annotation with all search details."""
        lines = []
        
        # Status
        lines.append(f"**Typesense:** {status}")
        
        # Query
        if ctx.query_text:
            lines.append("")
            lines.append(f"**Query:** {ctx.query_text}")

        # Esperado
        lines.append("")
        lines.append(f"**Esperado({ctx.total_expected}):**")
        for i, doc_id in enumerate(ctx.golden_docs, 1):
            lines.append(ctx.get_numbered_doc(i, doc_id, include_id=True))

        # Retornado
        lines.append("")
        lines.append(f"**Retornado({ctx.total_returned}):**")
        if ctx.has_returned_docs:
            for i, doc_id in enumerate(ctx.returned_ids[:10], 1):
                is_match = ctx.is_match(doc_id)
                lines.append(ctx.get_numbered_doc(i, doc_id, include_id=True, bold=is_match))
            if ctx.total_returned > 10:
                lines.append(f"... +{ctx.total_returned - 10} mais")
        else:
            lines.append("Nenhum")

        # Match
        lines.append("")
        lines.append(f"**Match({ctx.total_matched}/{ctx.total_expected}):**")
        if ctx.matched:
            for i, doc_id in enumerate(ctx.matched, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        else:
            lines.append("Nenhum")

        # Miss
        lines.append("")
        lines.append(f"**Miss({ctx.total_missing}/{ctx.total_expected}):**")
        if ctx.missing:
            for i, doc_id in enumerate(ctx.missing, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        else:
            lines.append("Nenhum")
        
        # Metric description
        lines.append("")
        lines.append("---")
        lines.append("*Typesense Activate: 1 se a ferramenta de busca foi chamada, 0 caso contrario.*")

        return "\n".join(lines)
