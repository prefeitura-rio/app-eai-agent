# -*- coding: utf-8 -*-
"""
TypesenseRecallEvaluator - Measures the proportion of golden documents found.

Score = matched_docs / expected_docs
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


class TypesenseRecallEvaluator(BaseTypesenseEvaluator):
    """
    Measures recall: what proportion of expected documents were found.
    
    Score = matched_docs / total_expected_docs
    """

    name = "typesense_recall"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute recall score and build annotation."""
        score = ctx.total_matched / ctx.total_expected if ctx.total_expected > 0 else 0.0
        
        lines = []
        lines.append(f"**Recall:** {ctx.total_matched}/{ctx.total_expected} ({score:.0%})")
        
        if ctx.matched:
            lines.append("")
            lines.append("**Encontrados:**")
            for i, doc_id in enumerate(ctx.matched, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        
        if ctx.missing:
            lines.append("")
            lines.append("**Faltando:**")
            for i, doc_id in enumerate(ctx.missing, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        
        lines.append("")
        lines.append("---")
        lines.append("*Recall: Proporcao de documentos esperados que foram encontrados. Formula: encontrados / esperados.*")
        
        return (score, "\n".join(lines))
