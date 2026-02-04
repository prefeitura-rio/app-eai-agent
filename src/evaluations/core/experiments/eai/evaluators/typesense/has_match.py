# -*- coding: utf-8 -*-
"""
TypesenseHasMatchEvaluator - Binary metric to check if any golden document was found.

Score = 1 if any match, 0 otherwise
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


class TypesenseHasMatchEvaluator(BaseTypesenseEvaluator):
    """
    Binary evaluator that checks if at least one golden document appears in the search results.
    """

    name = "typesense_has_match"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute has_match score and build annotation."""
        has_match = ctx.total_matched > 0
        score = 1 if has_match else 0
        
        lines = []
        
        if has_match:
            lines.append(f"**Resultado:** Sim ({ctx.total_matched} doc(s) encontrado(s))")
            lines.append("")
            lines.append("**Docs encontrados:**")
            for i, doc_id in enumerate(ctx.matched, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        else:
            if not ctx.has_returned_docs:
                lines.append("**Resultado:** Nao (nenhuma busca executada)")
            else:
                lines.append(f"**Resultado:** Nao (0/{ctx.total_expected} docs encontrados)")
        
        lines.append("")
        lines.append("---")
        lines.append("*Has Match: 1 se pelo menos um documento esperado foi retornado, 0 caso contrario.*")
        
        return (score, "\n".join(lines))
