# -*- coding: utf-8 -*-
"""
TypesensePrecisionEvaluator - Measures the proportion of returned documents that are relevant.

Score = relevant_returned_docs / total_returned_docs
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


class TypesensePrecisionEvaluator(BaseTypesenseEvaluator):
    """
    Measures precision: what proportion of returned documents are relevant.
    
    Score = relevant_docs_in_results / total_docs_returned
    """

    name = "typesense_precision"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute precision score and build annotation."""
        lines = []
        
        if not ctx.has_returned_docs:
            score = 0.0
            lines.append("**Precision:** 0% (nenhum documento retornado)")
        else:
            score = ctx.total_matched / ctx.total_returned
            lines.append(f"**Precision:** {ctx.total_matched}/{ctx.total_returned} ({score:.0%})")
            if ctx.matched:
                lines.append("")
                lines.append("**Relevantes retornados:**")
                for i, doc_id in enumerate(ctx.matched, 1):
                    lines.append(ctx.get_numbered_doc(i, doc_id))
        
        lines.append("")
        lines.append("---")
        lines.append("*Precision: Proporcao de documentos retornados que sao relevantes. Formula: relevantes / retornados.*")
        
        return (score, "\n".join(lines))
