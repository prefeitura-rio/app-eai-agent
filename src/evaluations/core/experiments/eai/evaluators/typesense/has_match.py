# -*- coding: utf-8 -*-
"""
TypesenseHasMatchEvaluator - Binary metric to check if any golden document was found.

Scenarios:
    1. Has match between expected and returned      -> Score 1
    2. No match between expected and returned       -> Score 0
    3. No docs defined + has docs returned          -> Score None
    4. No docs defined + no docs returned           -> Score None

"Has docs defined" is determined by: golden_documents_list is defined and not empty
"Has docs returned" is determined by: search results exist with Typesense format
"""

from typing import Dict, List

from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
)
from src.evaluations.core.experiments.eai.evaluators.typesense.base import (
    BaseTypesenseEvaluator,
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
            # Parse golden documents
            golden_docs = self.parse_golden_documents(
                getattr(task, "golden_documents_list", None)
            )
            golden_doc_names = self.parse_golden_document_names(
                getattr(task, "golden_documents_list_names", None)
            )
            id_to_name = self._create_id_to_name_mapping(golden_docs, golden_doc_names)

            # Extract returned documents and queries
            search_results = self.extract_search_results(agent_response)
            returned_docs = self._get_all_returned_docs(search_results)
            queries = self.extract_search_queries(agent_response)

            has_docs_defined = len(golden_docs) > 0
            has_docs_returned = len(returned_docs["ids"]) > 0

            # Apply scenario logic
            score, annotation = self._evaluate_scenario(
                has_docs_defined=has_docs_defined,
                has_docs_returned=has_docs_returned,
                golden_docs=golden_docs,
                returned_docs=returned_docs,
                id_to_name=id_to_name,
                agent_response=agent_response,
                queries=queries,
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

    def _get_all_returned_docs(self, search_results) -> Dict:
        """Extract all returned document IDs and titles from search results."""
        all_ids = []
        id_to_title = {}

        for result in search_results:
            for doc_id, title in zip(result.doc_ids, result.doc_titles):
                if doc_id not in id_to_title:
                    all_ids.append(doc_id)
                    id_to_title[doc_id] = title

        return {
            "ids": all_ids,
            "id_to_title": id_to_title,
        }

    def _evaluate_scenario(
        self,
        has_docs_defined: bool,
        has_docs_returned: bool,
        golden_docs: List[str],
        returned_docs: Dict,
        id_to_name: Dict[str, str],
        agent_response: AgentResponse,
        queries: List[str],
    ) -> tuple:
        """
        Evaluate based on the 4 scenarios:

        1. Has match between expected and returned      -> Score 1
        2. No match between expected and returned       -> Score 0
        3. No docs defined + has docs returned          -> Score None
        4. No docs defined + no docs returned           -> Score None

        Returns:
            tuple: (score, annotation)
        """
        # Scenarios 3 and 4: No docs defined -> Score None
        if not has_docs_defined:
            if has_docs_returned:
                # Show returned docs even without golden docs
                annotation = self._build_returned_only_annotation(returned_docs, queries)
            else:
                annotation = (
                    "Sem documentos esperados definidos (nenhuma busca executada)"
                )
            return (None, annotation)

        # Has docs defined - check for matches
        golden_set = set(golden_docs)
        returned_set = set(returned_docs["ids"])

        matched_docs = list(golden_set.intersection(returned_set))
        missing_docs = list(golden_set - returned_set)

        has_match = len(matched_docs) > 0

        # Build annotation
        annotation = self._build_annotation(
            golden_docs=golden_docs,
            returned_docs=returned_docs,
            matched_docs=matched_docs,
            missing_docs=missing_docs,
            id_to_name=id_to_name,
            has_docs_returned=has_docs_returned,
            agent_response=agent_response,
            queries=queries,
        )

        if has_match:
            # Scenario 1: Has match -> Score 1
            return (1, annotation)
        else:
            # Scenario 2: No match -> Score 0
            return (0, annotation)

    def _create_id_to_name_mapping(
        self, golden_docs: List[str], golden_doc_names: List[str]
    ) -> Dict[str, str]:
        """Create a mapping from document IDs to their names."""
        id_to_name = {}
        for i, doc_id in enumerate(golden_docs):
            if i < len(golden_doc_names) and golden_doc_names[i]:
                id_to_name[doc_id] = golden_doc_names[i]
        return id_to_name

    def _get_doc_display(
        self,
        doc_id: str,
        id_to_name: Dict[str, str],
        id_to_title: Dict[str, str],
        include_full_id: bool = False,
    ) -> str:
        """Get display string for a document."""
        # Priority: golden name > returned title > ID
        name = id_to_name.get(doc_id) or id_to_title.get(doc_id)

        if include_full_id:
            if name:
                return f"{name} ({doc_id})"
            else:
                return doc_id
        else:
            if name:
                return name
            else:
                return doc_id[:8] if len(doc_id) > 8 else doc_id

    def _build_returned_only_annotation(
        self, returned_docs: Dict, queries: List[str]
    ) -> str:
        """Build annotation showing only returned docs (when no golden docs defined)."""
        lines = []
        
        # Query no topo
        if queries:
            query_text = queries[0] if len(queries) == 1 else " | ".join(queries)
            lines.append(f"**Query:** {query_text}")
            lines.append("")
        
        total_returned = len(returned_docs["ids"])
        lines.append(f"**Retornado({total_returned}):**")
        id_to_title = returned_docs["id_to_title"]

        for doc_id in returned_docs["ids"][:10]:
            title = id_to_title.get(doc_id, "")
            if title:
                lines.append(f"{title} ({doc_id})")
            else:
                lines.append(doc_id)
        if total_returned > 10:
            lines.append(f"... +{total_returned - 10} mais")

        return "\n".join(lines)

    def _build_annotation(
        self,
        golden_docs: List[str],
        returned_docs: Dict,
        matched_docs: List[str],
        missing_docs: List[str],
        id_to_name: Dict[str, str],
        has_docs_returned: bool,
        agent_response: AgentResponse,
        queries: List[str],
    ) -> str:
        """Build markdown annotation in list format with counts."""
        lines = []
        id_to_title = returned_docs["id_to_title"]
        
        # Query no topo
        if queries:
            query_text = queries[0] if len(queries) == 1 else " | ".join(queries)
            lines.append(f"**Query:** {query_text}")
            lines.append("")
        
        total_expected = len(golden_docs)
        total_returned = len(returned_docs["ids"])
        total_matched = len(matched_docs)
        total_missing = len(missing_docs)

        # Esperado
        lines.append(f"**Esperado({total_expected}):**")
        for doc_id in golden_docs:
            display = self._get_doc_display(
                doc_id, id_to_name, id_to_title, include_full_id=True
            )
            lines.append(display)

        # Retornado (blank line before new section)
        lines.append("")
        lines.append(f"**Retornado({total_returned}):**")
        if has_docs_returned:
            for doc_id in returned_docs["ids"][:10]:
                display = self._get_doc_display(
                    doc_id, id_to_name, id_to_title, include_full_id=True
                )
                lines.append(display)
            if total_returned > 10:
                lines.append(f"... +{total_returned - 10} mais")
        else:
            if self.has_search_been_executed(agent_response):
                lines.append("Busca executada mas sem resultados Typesense")
            else:
                lines.append("Nenhuma busca executada")

        # Match
        lines.append("")
        lines.append(f"**Match({total_matched}/{total_expected}):**")
        if matched_docs:
            for doc_id in matched_docs:
                display = self._get_doc_display(
                    doc_id, id_to_name, id_to_title, include_full_id=False
                )
                lines.append(display)
        else:
            lines.append("Nenhum")

        # Miss
        lines.append("")
        lines.append(f"**Miss({total_missing}/{total_expected}):**")
        if missing_docs:
            for doc_id in missing_docs:
                display = self._get_doc_display(
                    doc_id, id_to_name, id_to_title, include_full_id=False
                )
                lines.append(display)
        else:
            lines.append("Nenhum")

        return "\n".join(lines)
