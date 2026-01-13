# -*- coding: utf-8 -*-
"""
TypesenseMRREvaluator - Mean Reciprocal Rank metric.

Score = 1 / position_of_first_match
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


class TypesenseMRREvaluator(BaseTypesenseEvaluator):
    """
    Mean Reciprocal Rank evaluator.
    
    Score = 1 / position_of_first_relevant_document
    """

    name = "typesense_mrr"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute MRR score and build annotation."""
        first_position, first_match_id = ctx.find_first_match_position()
        
        lines = []
        
        if first_position:
            score = 1.0 / first_position
            doc_display = ctx.get_doc_display(first_match_id) if first_match_id else "?"
            lines.append(f"**MRR:** 1/{first_position} = {score:.2f}")
            lines.append(f"**Primeiro match:** {doc_display} (posicao {first_position})")
        else:
            score = 0.0
            if not ctx.has_returned_docs:
                lines.append("**MRR:** 0.00 (nenhum resultado retornado)")
            else:
                lines.append(f"**MRR:** 0.00 (nenhum match em {ctx.total_returned} docs)")
        
        lines.append("")
        lines.append("---")
        lines.append("*MRR (Mean Reciprocal Rank): 1 dividido pela posicao do primeiro documento relevante. Quanto mais alto na lista, maior o score.*")
        
        return (score, "\n".join(lines))
