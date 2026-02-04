# -*- coding: utf-8 -*-
"""
TypesenseAllMatchEvaluator - Binary metric to check if ALL golden documents were found.

Score = 1 if ALL golden docs found, 0 otherwise
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


class TypesenseAllMatchEvaluator(BaseTypesenseEvaluator):
    """
    Binary evaluator that checks if ALL golden documents appear in the search results.
    
    More strict than has_match - requires 100% coverage.
    """

    name = "typesense_all_match"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute all_match score and build annotation."""
        all_found = ctx.total_missing == 0
        score = 1 if all_found else 0
        
        lines = []
        
        if all_found:
            lines.append(f"**Resultado:** Sim (todos os {ctx.total_expected} docs encontrados)")
        else:
            lines.append(f"**Resultado:** Nao ({ctx.total_matched}/{ctx.total_expected} encontrados)")
            lines.append("")
            lines.append("**Faltando:**")
            for i, doc_id in enumerate(ctx.missing, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        
        lines.append("")
        lines.append("---")
        lines.append("*All Match: 1 se TODOS os documentos esperados foram encontrados, 0 caso contrario.*")
        
        return (score, "\n".join(lines))
