# -*- coding: utf-8 -*-
"""
Base class for Typesense search evaluators.
Contains shared utility methods for parsing golden documents and extracting search results.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.evaluations.core.eval import (
    AgentResponse,
    BaseOneTurnEvaluator,
)


@dataclass
class SearchResult:
    """Represents a single search call's results."""
    doc_ids: List[str]
    doc_titles: List[str]
    raw_documents: List[Dict[str, Any]]


class BaseTypesenseEvaluator(BaseOneTurnEvaluator):
    """
    Base class for all Typesense search evaluators.
    
    Provides common utility methods for:
    - Parsing golden documents from various formats
    - Extracting search results from agent responses
    - Validating Typesense response format
    """

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
