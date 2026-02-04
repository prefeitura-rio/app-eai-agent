# -*- coding: utf-8 -*-
"""
TypesenseTopKMatchEvaluator - Binary metric to check if any golden doc is in top K results.

Score = 1 if at least one golden doc is in top K, 0 otherwise
Default K = 3
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


class TypesenseTopKMatchEvaluator(BaseTypesenseEvaluator):
    """
    Binary evaluator that checks if at least one golden document is in the top K results.
    
    Default K = 3
    """

    name = "typesense_top3_match"
    K = 3  # Top K results to consider

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            ctx = self.build_context(agent_response, task)
            return self.evaluate_scenario(ctx, self._compute_score_and_annotation)
        except Exception as e:
            return self.error_result(e)

    def _compute_score_and_annotation(self, ctx: TypesenseEvalContext) -> tuple:
        """Compute top-k match score and build annotation."""
        top_k_ids = ctx.returned_ids[:self.K]
        top_k_set = set(top_k_ids)
        matched_in_top_k = ctx.golden_set.intersection(top_k_set)
        
        has_match_in_top_k = len(matched_in_top_k) > 0
        score = 1 if has_match_in_top_k else 0
        
        lines = []

        if has_match_in_top_k:
            lines.append(f"**Resultado:** Sim (match no Top {self.K})")
            lines.append("")
            lines.append(f"**No Top {self.K}:**")
            for i, doc_id in enumerate(matched_in_top_k, 1):
                lines.append(ctx.get_numbered_doc(i, doc_id))
        else:
            first_position, first_match_id = ctx.find_first_match_position()
            if first_position:
                doc_display = ctx.get_doc_display(first_match_id) if first_match_id else "?"
                lines.append(f"**Resultado:** Nao (primeiro match na posicao {first_position})")
                lines.append(f"**Primeiro match:** {doc_display}")
            elif not ctx.has_returned_docs:
                lines.append(f"**Resultado:** Nao (nenhum resultado retornado)")
            else:
                lines.append(f"**Resultado:** Nao (nenhum match em {ctx.total_returned} docs)")
        
        lines.append("")
        lines.append("---")
        lines.append(f"*Top {self.K} Match: 1 se pelo menos um documento esperado esta entre os {self.K} primeiros resultados, 0 caso contrario.*")
        
        return (score, "\n".join(lines))
