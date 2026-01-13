# -*- coding: utf-8 -*-
"""
Base class for Typesense search evaluators.
Contains shared utility methods for parsing golden documents and extracting search results.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from src.evaluations.core.eval import (
    AgentResponse,
    EvaluationTask,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


@dataclass
class SearchResult:
    """Represents a single search call's results."""
    doc_ids: List[str]
    doc_titles: List[str]
    raw_documents: List[Dict[str, Any]]


@dataclass
class TypesenseEvalContext:
    """
    Common evaluation context extracted from task and agent response.
    Shared across all Typesense evaluators.
    """
    # Golden data
    golden_docs: List[str]
    golden_doc_names: List[str]
    id_to_name: Dict[str, str]
    
    # Returned data
    search_results: List[SearchResult]
    returned_ids: List[str]
    returned_id_to_title: Dict[str, str]
    queries: List[str]
    
    # Computed sets for matching
    golden_set: Set[str] = field(default_factory=set)
    returned_set: Set[str] = field(default_factory=set)
    matched: Set[str] = field(default_factory=set)
    missing: Set[str] = field(default_factory=set)
    
    # Flags
    has_golden_docs: bool = False
    has_returned_docs: bool = False
    
    def __post_init__(self):
        self.golden_set = set(self.golden_docs)
        self.returned_set = set(self.returned_ids)
        self.matched = self.golden_set.intersection(self.returned_set)
        self.missing = self.golden_set - self.returned_set
        self.has_golden_docs = len(self.golden_docs) > 0
        self.has_returned_docs = len(self.returned_ids) > 0
    
    @property
    def total_expected(self) -> int:
        return len(self.golden_docs)
    
    @property
    def total_returned(self) -> int:
        return len(self.returned_ids)
    
    @property
    def total_matched(self) -> int:
        return len(self.matched)
    
    @property
    def total_missing(self) -> int:
        return len(self.missing)
    
    @property
    def query_text(self) -> Optional[str]:
        """Formatted query string."""
        if not self.queries:
            return None
        return self.queries[0] if len(self.queries) == 1 else " | ".join(self.queries)
    
    def get_doc_display(self, doc_id: str, include_id: bool = False) -> str:
        """Get display string for a document."""
        name = self.id_to_name.get(doc_id) or self.returned_id_to_title.get(doc_id)
        if include_id:
            if name:
                return f"{name} ({doc_id})"
            return doc_id
        else:
            if name:
                return name
            return doc_id[:8] if len(doc_id) > 8 else doc_id
    
    def get_numbered_doc(
        self, 
        index: int, 
        doc_id: str, 
        include_id: bool = False,
        bold: bool = False,
    ) -> str:
        """Get numbered display string for a document."""
        display = self.get_doc_display(doc_id, include_id)
        if bold:
            return f"{index}. **{display}**"
        return f"{index}. {display}"
    
    def is_match(self, doc_id: str) -> bool:
        """Check if doc_id is in the matched set."""
        return doc_id in self.matched
    
    def find_first_match_position(self) -> tuple[Optional[int], Optional[str]]:
        """Find position of first golden doc in returned results (1-indexed)."""
        for i, doc_id in enumerate(self.returned_ids):
            if doc_id in self.golden_set:
                return (i + 1, doc_id)
        return (None, None)


class BaseTypesenseEvaluator(BaseOneTurnEvaluator):
    """
    Base class for all Typesense search evaluators.
    
    Provides common utility methods for:
    - Parsing golden documents from various formats
    - Extracting search results from agent responses
    - Validating Typesense response format
    - Building evaluation context
    """

    def build_context(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> TypesenseEvalContext:
        """
        Build common evaluation context from task and agent response.
        This extracts and processes all data needed by evaluators.
        """
        # Parse golden documents
        golden_docs = self.parse_golden_documents(
            getattr(task, "golden_documents_list", None)
        )
        golden_doc_names = self.parse_golden_document_names(
            getattr(task, "golden_documents_list_names", None)
        )
        
        # Create ID to name mapping
        id_to_name: Dict[str, str] = {}
        for i, doc_id in enumerate(golden_docs):
            if i < len(golden_doc_names) and golden_doc_names[i]:
                id_to_name[doc_id] = golden_doc_names[i]
        
        # Extract search results
        search_results = self.extract_search_results(agent_response)
        
        # Extract returned IDs and titles
        returned_ids: List[str] = []
        returned_id_to_title: Dict[str, str] = {}
        seen: Set[str] = set()
        for result in search_results:
            for doc_id, title in zip(result.doc_ids, result.doc_titles):
                if doc_id not in seen:
                    returned_ids.append(doc_id)
                    returned_id_to_title[doc_id] = title
                    seen.add(doc_id)
        
        # Extract queries
        queries = self.extract_search_queries(agent_response)
        
        return TypesenseEvalContext(
            golden_docs=golden_docs,
            golden_doc_names=golden_doc_names,
            id_to_name=id_to_name,
            search_results=search_results,
            returned_ids=returned_ids,
            returned_id_to_title=returned_id_to_title,
            queries=queries,
        )

    def no_golden_docs_result(self) -> EvaluationResult:
        """Return standard result when no golden docs are defined."""
        return EvaluationResult(
            score=None,
            annotations="Sem documentos esperados definidos",
            has_error=False,
            error_message=None,
        )

    def error_result(self, error: Exception) -> EvaluationResult:
        """Return standard error result."""
        return EvaluationResult(
            score=None,
            annotations=None,
            has_error=True,
            error_message=str(error),
        )

    def success_result(self, score: float, annotations: str) -> EvaluationResult:
        """Return standard success result."""
        return EvaluationResult(
            score=score,
            annotations=annotations,
            has_error=False,
            error_message=None,
        )

    def parse_golden_documents(self, golden_documents_list: Any) -> List[str]:
        """
        Parse the list of expected (golden) documents.
        
        Handles various input formats:
        - String with brackets: "['uuid1', 'uuid2']"
        - String with commas: "uuid1, uuid2"
        - List of strings: ["uuid1", "uuid2"]
        
        Returns:
            List of document IDs (empty list if no valid documents found)
        """
        if not golden_documents_list:
            return []
        
        # If it's a string, parse it
        if isinstance(golden_documents_list, str):
            golden_documents_list = golden_documents_list.strip()
            if not golden_documents_list:
                return []
            
            # Remove outer brackets if present (handles "['uuid']" format)
            if golden_documents_list.startswith('[') and golden_documents_list.endswith(']'):
                golden_documents_list = golden_documents_list[1:-1].strip()
            
            # Split by comma, semicolon, or whitespace
            if ',' in golden_documents_list:
                docs = golden_documents_list.split(',')
            elif ';' in golden_documents_list:
                docs = golden_documents_list.split(';')
            else:
                docs = golden_documents_list.split()
            
            # Clean each doc ID: strip whitespace and quotes
            cleaned_docs = []
            for doc in docs:
                doc = doc.strip()
                # Remove surrounding quotes (single or double)
                if (doc.startswith("'") and doc.endswith("'")) or \
                   (doc.startswith('"') and doc.endswith('"')):
                    doc = doc[1:-1]
                if doc:
                    cleaned_docs.append(doc)
            
            return cleaned_docs
        
        # If it's already a list, clean each item
        if isinstance(golden_documents_list, list):
            cleaned_docs = []
            for doc in golden_documents_list:
                doc_str = str(doc).strip()
                # Remove surrounding quotes
                if (doc_str.startswith("'") and doc_str.endswith("'")) or \
                   (doc_str.startswith('"') and doc_str.endswith('"')):
                    doc_str = doc_str[1:-1]
                if doc_str:
                    cleaned_docs.append(doc_str)
            return cleaned_docs
        
        return []

    def extract_search_results(self, agent_response: AgentResponse) -> List[SearchResult]:
        """
        Extract all valid Typesense search results from the agent's reasoning trace.
        
        Looks for tool_return_message with either:
        - 'response' key (google_search tool)
        - 'documents' key (dharma_search_tool)
        
        Returns:
            List of SearchResult objects, one for each valid search call
        """
        search_results: List[SearchResult] = []

        if not agent_response or not agent_response.reasoning_trace:
            return search_results
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            # Handle case where content might not be a dict
            if not isinstance(step.content, dict):
                continue
                
            tool_return = step.content.get("tool_return", {})
            
            # Validate Typesense format
            if not self._is_valid_typesense_format(tool_return):
                continue
            
            # Extract documents (supports both 'response' and 'documents' keys)
            docs_list = tool_return.get("response") or tool_return.get("documents", [])
            
            doc_ids = [doc.get("id") for doc in docs_list if doc.get("id")]
            doc_titles = [doc.get("title", "") for doc in docs_list]
            
            if doc_ids:
                search_results.append(SearchResult(
                    doc_ids=doc_ids,
                    doc_titles=doc_titles,
                    raw_documents=docs_list,
                ))
        
        return search_results

    def _is_valid_typesense_format(self, tool_return: Any) -> bool:
        """
        Validate that the tool_return has a valid Typesense response format.
        
        Expected format:
        {
            "response": [  # or "documents"
                {"id": "...", "title": "...", ...},
                ...
            ]
        }
        
        Returns:
            True if valid Typesense format, False otherwise
        """
        if not isinstance(tool_return, dict):
            return False
            
        # Check for 'response' or 'documents' key
        docs_list = tool_return.get("response") or tool_return.get("documents")
        
        if not docs_list:
            return False
        
        if not isinstance(docs_list, list):
            return False
        
        if len(docs_list) == 0:
            return False
        
        # Validate that all items have 'id' and 'title'
        return all(
            isinstance(item, dict) and "id" in item and "title" in item
            for item in docs_list
        )

    def has_search_been_executed(self, agent_response: AgentResponse) -> bool:
        """Check if any search tool was called."""
        if not agent_response or not agent_response.reasoning_trace:
            return False
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_call_message":
                continue
            if isinstance(step.content, dict):
                tool_name = step.content.get("name", "")
                if tool_name in ["google_search", "dharma_search_tool"]:
                    return True
        
        return False

    def extract_search_queries(self, agent_response: AgentResponse) -> List[str]:
        """
        Extract all search queries from the agent's reasoning trace.
        
        Looks for tool_call_message with google_search or dharma_search_tool
        and extracts the query parameter.
        
        Returns:
            List of query strings
        """
        queries: List[str] = []
        
        if not agent_response or not agent_response.reasoning_trace:
            return queries
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_call_message":
                continue
            
            if not isinstance(step.content, dict):
                continue
            
            tool_name = step.content.get("name", "")
            if tool_name not in ["google_search", "dharma_search_tool"]:
                continue
            
            # Extract query from arguments
            args = step.content.get("arguments", {})
            if isinstance(args, dict):
                query = args.get("query") or args.get("search_query") or args.get("q")
                if query:
                    queries.append(str(query))
        
        return queries

    def parse_golden_document_names(self, golden_doc_names: Any) -> List[str]:
        """
        Parse the list of golden document names.
        
        Unlike IDs which are UUIDs, names are human-readable strings that
        may or may not be quoted. This method handles:
        - Single name: "Histórico de Tarifas"
        - Comma-separated names: "Name 1,Name 2,Name 3"
        - Empty/None input
        
        Returns:
            List of document names (empty list if no valid names found)
        """
        if not golden_doc_names:
            return []
        
        if isinstance(golden_doc_names, str):
            golden_doc_names = golden_doc_names.strip()
            if not golden_doc_names:
                return []
            
            # Split by comma (names are comma-separated in the dataset)
            names = [name.strip() for name in golden_doc_names.split(',')]
            return [name for name in names if name]
        
        if isinstance(golden_doc_names, list):
            return [str(name).strip() for name in golden_doc_names if name]
        
        return []

    # =========================================================================
    # Scenario Evaluation Methods
    # =========================================================================

    def evaluate_scenario(
        self,
        ctx: TypesenseEvalContext,
        compute_score_and_annotation,
    ) -> EvaluationResult:
        """
        Evaluate based on the 4 scenarios. All Typesense evaluators should use this.

        Scenarios:
            1. Has golden docs + has results -> Score from compute_score_and_annotation()
            2. Has golden docs + no results  -> Score from compute_score_and_annotation()
            3. No golden docs + has results  -> Score None
            4. No golden docs + no results   -> Score None

        Args:
            ctx: TypesenseEvalContext with all evaluation data
            compute_score_and_annotation: Callable that receives ctx and returns (score, annotation)

        Returns:
            EvaluationResult with score and annotation
        """
        # Scenarios 3 and 4: No golden docs defined -> Score None
        if not ctx.has_golden_docs:
            return EvaluationResult(
                score=None,
                annotations="Sem documentos esperados definidos",
                has_error=False,
                error_message=None,
            )

        # Scenarios 1 and 2: Has golden docs defined
        score, annotation = compute_score_and_annotation(ctx)
        return self.success_result(score, annotation)
