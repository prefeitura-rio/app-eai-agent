"""
Phoenix Trace Processor - Processamento Eficiente de Spans com SpanQuery

Este script implementa um processador de traces do Phoenix que utiliza queries direcionadas
para buscar e processar spans de forma eficiente, em vez de baixar datasets completos.

FUNCIONALIDADES PRINCIPAIS:
- Busca spans específicos usando SpanQuery (Agent.step, Agent._handle_ai_response, etc.)
- Extrai e processa dados de queries, respostas de modelos, ferramentas de busca e memória core
- Classifica spans automaticamente baseado no tipo de operação (AGENT, LLM, TOOL, CHAIN)
- Modifica IDs de trace e span para upload seguro no Phoenix (CONFIGURÁVEL!)

MODIFICAÇÃO DE IDs (trace_id e span_id) - CONFIGURÁVEL:
O script pode modificar os IDs dos traces e spans antes do upload para o Phoenix.
Esta funcionalidade é CONFIGURÁVEL através do parâmetro modify_ids=True/False.

COMO FUNCIONA:
- trace_id original: "abc123def" → modificado: "abc123dea" (último caractere alterado)
- span_id original: "xyz456789" → modificado: "xyz456789a"
- parent_id é atualizado para manter a hierarquia correta entre spans

CONFIGURAÇÃO:
- modify_ids=True (RECOMENDADO): Modifica IDs para evitar conflitos
- modify_ids=False: Preserva IDs originais

MOTIVOS PARA MODIFICAÇÃO DOS IDs:
1. EVITAR CONFLITOS: Previne conflitos de ID ao fazer upload de spans processados
2. DADOS ÚNICOS: Garante que os spans processados tenham IDs únicos no Phoenix
3. PRESERVAR ORIGINAL: Não sobrescreve dados originais já existentes no Phoenix
4. RELACIONAMENTOS: Mantém a estrutura pai-filho entre spans após modificação

FLUXO DE PROCESSAMENTO:
1. Buscar dados com queries direcionadas (fetch_questions, fetch_responses, etc.)
2. Preparar DataFrames com colunas padronizadas
3. Combinar todos os dados em um DataFrame único
4. Filtrar por trace_id específico (se fornecido)
5. Modificar IDs para compatibilidade com Phoenix (SE modify_ids=True)
6. Limpar dados (remover None/NaN)
7. Fazer upload para Phoenix
"""

import re
import json
import pandas as pd
import numpy as np
import phoenix as px
from typing import Optional, List, Any
from phoenix.trace.dsl import SpanQuery


class PhoenixTraceProcessor:
    """
    Processes and enriches Phoenix trace data with span classification and cleaning utilities.

    This class provides methods to classify spans according to OpenInference conventions,
    filter unwanted spans, and clean data structures by removing None values.
    Uses efficient SpanQuery approach instead of downloading entire datasets.

    Note: Consider adding comprehensive unit tests to verify all processing methods
    work correctly across different trace scenarios and edge cases.
    """

    def __init__(self, phoenix_endpoint: str, project_name: str = "default"):
        """
        Initialize the Phoenix trace processor.

        Args:
            phoenix_endpoint (str): The Phoenix server endpoint URL
            project_name (str): The Phoenix project name to query

        Note: Consider adding unit tests to verify client initialization.
        """
        self.phoenix_client = px.Client(endpoint=phoenix_endpoint)
        self.project_name = project_name

    def extrair_valor(self, raw_text: str, label: str) -> Optional[str]:
        """
        Extracts value from raw text using regex pattern matching.

        Args:
            raw_text (str): Raw text to extract from
            label (str): Label to search for (e.g., "Persona", "Human")

        Returns:
            Optional[str]: Extracted and cleaned text or None if not found

        Note: Consider adding unit tests to verify extraction across different text formats.
        """
        if raw_text is None or pd.isna(raw_text):
            return None

        pattern = rf"{label}\(value=(?P<quote>['\"])(.*?)(?P=quote)"
        match = re.search(pattern, raw_text, re.DOTALL)

        if match:
            texto = match.group(2)
            texto = texto.replace("\\n", " ").strip()
            texto = re.sub(" +", " ", texto)
            return texto

        return None

    def extrair_query(self, raw_text: str) -> Optional[str]:
        """
        Extracts query from raw text using regex pattern matching.

        Args:
            raw_text (str): Raw text containing query information

        Returns:
            Optional[str]: Extracted query or None if not found

        Note: Consider adding unit tests to verify query extraction.
        """
        if raw_text is None or pd.isna(raw_text):
            return None

        match = re.search(r'"query": "(.*?)"', raw_text)
        return match.group(1) if match else None

    def parse_response(self, response: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parses response to extract tool call and message content.

        Args:
            response (str): Raw response text

        Returns:
            tuple[Optional[str], Optional[str]]: Tool name and message content
        """
        if response is None or pd.isna(response):
            return None, None

        # Convert to string to handle numpy/pandas scalar types
        response_str = str(response) if response is not None else ""
        if not response_str or response_str == "nan":
            return None, None

        tool_call_match = re.search(
            r"tool_calls=\[(.*?)\] role=", response_str, re.DOTALL
        )
        tool_call = tool_call_match.group(1) if tool_call_match else None

        if tool_call and "send_message" in tool_call:
            message_match = re.search(r"arguments='\{(.*)\}'", tool_call, re.DOTALL)
            if message_match:
                message = message_match.group(1)
                message = re.sub(
                    r'\s*"request_heartbeat":\s*(true|false)\s*,?', "", message
                ).strip()
                message = re.sub(r"^(\\n|\s)+|(\s|\\n)+$", "", message)
                message_final_match = re.search(
                    r'"message":\s*"(.+)"', message, re.DOTALL
                )
                message = message_final_match.group(1) if message_final_match else None
            else:
                message = None
        else:
            message = None

        tool_match = re.search(r"name='([^']+)'", tool_call) if tool_call else None
        tool = tool_match.group(1) if tool_match else None

        return tool, message

    def extrair_content(self, raw_text: str) -> Optional[str]:
        """
        Extracts content from raw text using regex pattern matching.

        Args:
            raw_text (str): Raw text to extract content from

        Returns:
            Optional[str]: Extracted content or None if not found

        Note: Consider adding unit tests to verify content extraction.
        """
        if raw_text is None or pd.isna(raw_text):
            return None

        match = re.search(r"(?:content|text)='(.*?)'", raw_text)
        return match.group(1) if match else None

    def fetch_questions(self) -> pd.DataFrame:
        """
        Fetches question spans using SpanQuery.

        Sempre faz reset_index para garantir que context.span_id seja coluna, nunca índice.

        Returns:
            pd.DataFrame: DataFrame contendo questions com as colunas necessárias.
        """
        query = (
            SpanQuery()
            .where("name =='Agent.step'")
            .select(
                "name",
                "context.trace_id",
                "context.span_id",
                "parent_id",
                "start_time",
                "end_time",
                "status_message",
                "status_code",
                "events",
            )
        )
        df = self.phoenix_client.query_spans(query, project_name=self.project_name)
        df = df.reset_index()

        return df

    def fetch_responses(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetches response spans and separates them em model responses e tools.

        Sempre faz reset_index para garantir que context.span_id seja coluna, nunca índice.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: Model responses e tool spans com as colunas necessárias
        """
        query = (
            SpanQuery()
            .where("name =='Agent._handle_ai_response'")
            .select(
                "name",
                "context.trace_id",
                "context.span_id",
                "parent_id",
                "start_time",
                "end_time",
                "status_message",
                "status_code",
                "events",
                "parameter.response_message",  # Needed for tool classification
            )
        )

        df = self.phoenix_client.query_spans(query, project_name=self.project_name)
        df = df.reset_index()

        if "parameter.response_message" in df.columns:
            df[["tool_call", "model_response"]] = df[
                "parameter.response_message"
            ].apply(lambda x: pd.Series(self.parse_response(x)))
        else:
            df["tool_call"] = None
            df["model_response"] = None

        model_response = df[df["tool_call"] == "send_message"].copy()
        tools = df[df["tool_call"].isin(["google_search", "typesense_search"])].copy()

        columns_to_keep = [
            "name",
            "context.trace_id",
            "context.span_id",
            "parent_id",
            "start_time",
            "end_time",
            "status_message",
            "status_code",
            "events",
        ]

        model_response = model_response[columns_to_keep]
        tools = tools[columns_to_keep]

        return model_response, tools

    def fetch_core_memory(self) -> pd.DataFrame:
        """
        Fetches core memory spans using SpanQuery.

        Sempre faz reset_index para garantir que context.span_id seja coluna, nunca índice.

        Returns:
            pd.DataFrame: DataFrame contendo core memory data com as colunas necessárias.
        """
        query = (
            SpanQuery()
            .where("name =='ToolExecutionSandbox.run_local_dir_sandbox'")
            .select(
                "name",
                "context.trace_id",
                "context.span_id",
                "parent_id",
                "start_time",
                "end_time",
                "status_message",
                "status_code",
                "events",
            )
        )

        df = self.phoenix_client.query_spans(query, project_name=self.project_name)
        return df.reset_index()

    def _prepare_dataframe(
        self, df: pd.DataFrame, name: str, span_kind: str, suffix: str
    ) -> pd.DataFrame:
        """
        Prepares a DataFrame with standard columns for processing.

        Args:
            df (pd.DataFrame): DataFrame to prepare
            name (str): Span name to assign
            span_kind (str): Span kind to assign
            suffix (str): Suffix for span ID generation

        Returns:
            pd.DataFrame: Prepared DataFrame with standard columns
        """
        if df.empty:
            return df

        prepared_df = df.copy()
        prepared_df["name"] = name
        prepared_df["span_kind"] = span_kind
        prepared_df["attributes.openinference.span.kind"] = span_kind

        return prepared_df

    def fetch_search_tools(self) -> pd.DataFrame:
        """
        Fetches search tool spans using SpanQuery.

        Sempre faz reset_index para garantir que context.span_id seja coluna, nunca índice.

        Returns:
            pd.DataFrame: DataFrame contendo search tool data com as colunas necessárias.
        """
        query = (
            SpanQuery()
            .where("name =='Agent._get_ai_reply'")
            .select(
                "name",
                "context.trace_id",
                "context.span_id",
                "parent_id",
                "start_time",
                "end_time",
                "status_message",
                "status_code",
                "events",
            )
        )

        df = self.phoenix_client.query_spans(query, project_name=self.project_name)
        return df.reset_index()

    def recursively_clean_nones(
        self,
        obj: Any,
        replacement: str = "",
        key_name: Optional[str] = None,
        keys_to_preserve_none: Optional[List[str]] = None,
    ) -> Any:
        """
        Recursively replaces None values and pandas scalar NA types in nested data structures.

        Args:
            obj: The object to clean (dict, list, numpy array, or scalar)
            replacement (str): Value to replace None/NaN with
            key_name (str): Current key name for preservation check
            keys_to_preserve_none (list): Keys where None values should be preserved

        Returns:
            Cleaned object with None/NaN values replaced

        Note: Consider adding unit tests for this function to ensure proper handling
        of edge cases and nested structures.
        """
        keys_to_preserve_none = keys_to_preserve_none or []

        if key_name in keys_to_preserve_none and obj is None:
            return None

        if isinstance(obj, dict):
            return {
                k: self.recursively_clean_nones(
                    v, replacement, k, keys_to_preserve_none
                )
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, np.ndarray)):
            iterable = obj.tolist() if isinstance(obj, np.ndarray) else obj
            return [
                self.recursively_clean_nones(
                    elem, replacement, None, keys_to_preserve_none
                )
                for elem in iterable
            ]
        elif obj is None or pd.isna(obj):
            return replacement
        return obj

    def clean_dataframe_nones(
        self, df: pd.DataFrame, keys_to_preserve_none: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Applies recursive None cleaning to all object-type columns in a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to clean
            keys_to_preserve_none (list): Column names where None values should be preserved

        Returns:
            pd.DataFrame: Cleaned DataFrame

        Note: Consider adding unit tests to verify None handling across different column types.
        """
        keys_to_preserve_none = keys_to_preserve_none or []
        cleaned_df = df.copy()

        for col in cleaned_df.select_dtypes(include="object").columns:
            preserve_none = [col] if col in keys_to_preserve_none else None
            cleaned_df[col] = cleaned_df[col].apply(
                lambda x: (
                    None
                    if col in keys_to_preserve_none
                    and not isinstance(x, (list, dict, np.ndarray))
                    and pd.isna(x)
                    else self.recursively_clean_nones(x, "", col, preserve_none)
                )
            )
        return cleaned_df

    def create_fake_spans(
        self, original_spans: pd.DataFrame, trace_id_suffix: str = "a"
    ) -> pd.DataFrame:
        """
        Creates modified spans by updating trace and span IDs for Phoenix upload.

        This is necessary to avoid ID conflicts when uploading processed spans to Phoenix.
        The function generates new unique IDs while maintaining parent-child relationships.
        Ensures that the modified IDs remain valid hexadecimal strings of appropriate length.

        Args:
            original_spans (pd.DataFrame): Original spans DataFrame.
            trace_id_suffix (str): A single hexadecimal character suffix (0-9, a-f).

        Returns:
            pd.DataFrame: Modified spans with new unique IDs ready for Phoenix upload.

        Note: Consider adding unit tests to verify ID modification logic and parent-child relationships.
        """
        fake_spans = original_spans.copy()

        if not (
            len(trace_id_suffix) == 1 and trace_id_suffix in "0123456789abcdefABCDEF"
        ):
            raise ValueError("trace_id_suffix must be a single hexadecimal character.")

        def modify_id(
            hex_id: Optional[str], expected_length: int, suffix: str
        ) -> Optional[str]:
            if pd.isna(hex_id) or hex_id is None:
                return None

            hex_id_str = str(hex_id)
            hex_id_str = re.sub(r"[^0-9a-fA-F]", "", hex_id_str)

            if len(hex_id_str) < expected_length:
                hex_id_str = hex_id_str.zfill(expected_length)

            if len(hex_id_str) > expected_length:
                base_id = hex_id_str[: expected_length - 1]
            elif len(hex_id_str) == expected_length:
                base_id = hex_id_str[:-1]
            else:
                base_id = hex_id_str.ljust(expected_length - 1, "0")

            modified = base_id + suffix
            return modified

        if "context.trace_id" in fake_spans.columns:
            fake_spans["context.trace_id"] = fake_spans["context.trace_id"].apply(
                lambda x: modify_id(x, 32, trace_id_suffix)
            )

        if "context.span_id" in fake_spans.columns:
            original_span_ids = fake_spans["context.span_id"].tolist()
            new_span_ids = [
                modify_id(span_id, 16, trace_id_suffix) for span_id in original_span_ids
            ]
            fake_spans["context.span_id"] = new_span_ids

            if not fake_spans.empty and "parent_id" in fake_spans.columns:
                fake_spans["parent_id"] = fake_spans["parent_id"].apply(
                    lambda pid: (
                        modify_id(pid, 16, trace_id_suffix) if pd.notna(pid) else None
                    )
                )
        return fake_spans

    def fetch_all_data(self) -> dict:
        """
        Fetches all span data from Phoenix using SpanQuery approach.

        Returns:
            dict: Dictionary containing all fetched data with keys:
                - questions: DataFrame with question spans
                - model_responses: DataFrame with model response spans
                - tools: DataFrame with tool spans
                - core_memory: DataFrame with core memory spans
                - search_tools: DataFrame with search tool spans
        """
        questions_df = self.fetch_questions()
        model_responses_df, tools_df = self.fetch_responses()
        core_memory_df = self.fetch_core_memory()
        search_tools_df = self.fetch_search_tools()

        return {
            "questions": questions_df,
            "model_responses": model_responses_df,
            "tools": tools_df,
            "core_memory": core_memory_df,
            "search_tools": search_tools_df,
        }

    def process_data(
        self,
        raw_data: dict,
        target_trace_id: Optional[str] = None,
        modify_ids: bool = True,
    ) -> pd.DataFrame:
        """
        Processes raw span data into a unified DataFrame ready for Phoenix upload.

        Args:
            raw_data (dict): Raw data dictionary from fetch_all_data()
            target_trace_id (Optional[str]): Specific trace ID to process
            modify_ids (bool): Whether to modify trace_id and span_id for Phoenix upload

        Returns:
            pd.DataFrame: Processed trace data with required columns
        """
        all_dfs = []

        questions_prepared = self._prepare_dataframe(
            raw_data["questions"], "Agent.step", "AGENT", "_q"
        )
        if not questions_prepared.empty:
            all_dfs.append(questions_prepared)

        model_responses_prepared = self._prepare_dataframe(
            raw_data["model_responses"], "Agent._handle_ai_response", "LLM", "_mr"
        )
        if not model_responses_prepared.empty:
            all_dfs.append(model_responses_prepared)

        tools_prepared = self._prepare_dataframe(
            raw_data["tools"], "Agent._handle_ai_response", "TOOL", "_t"
        )
        if not tools_prepared.empty:
            all_dfs.append(tools_prepared)

        core_memory_prepared = self._prepare_dataframe(
            raw_data["core_memory"],
            "ToolExecutionSandbox.run_local_dir_sandbox",
            "CHAIN",
            "_cm",
        )
        if not core_memory_prepared.empty:
            all_dfs.append(core_memory_prepared)

        search_tools_prepared = self._prepare_dataframe(
            raw_data["search_tools"], "Agent._get_ai_reply", "AGENT", "_st"
        )
        if not search_tools_prepared.empty:
            all_dfs.append(search_tools_prepared)

        if not all_dfs:
            return pd.DataFrame()

        combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)

        if target_trace_id:
            combined_df = combined_df[
                combined_df["context.trace_id"] == target_trace_id
            ]

        if combined_df.empty:
            return pd.DataFrame()

        if modify_ids:
            final_spans = self.create_fake_spans(combined_df)
        else:
            final_spans = combined_df

        final_spans = self.clean_events_column(final_spans)

        if target_trace_id:
            agent_spans = final_spans[
                final_spans["context.trace_id"] == target_trace_id
            ].sort_values("start_time", ascending=False)
        else:
            agent_spans = final_spans.sort_values(
                ["context.trace_id", "start_time"], ascending=[True, False]
            )

        agent_spans = self.clean_dataframe_nones(agent_spans, ["parent_id", "events"])

        return agent_spans

    def process_traces(
        self,
        target_trace_id: Optional[str] = None,
        modify_ids: bool = True,
    ) -> pd.DataFrame:
        """
        Complete trace processing pipeline using efficient SpanQuery approach.

        Args:
            target_trace_id (Optional[str]): Specific trace ID to process
            modify_ids (bool): Whether to modify trace_id and span_id for Phoenix upload

        Returns:
            pd.DataFrame: Processed trace data with required columns
        """
        raw_data = self.fetch_all_data()
        return self.process_data(raw_data, target_trace_id, modify_ids)

    def upload_traces(self, spans_df: pd.DataFrame) -> None:
        """
        Logs processed spans to Phoenix.

        Args:
            spans_df (pd.DataFrame): Processed spans to log

        Note: Consider adding unit tests to verify logging functionality.
        """
        self.phoenix_client.log_traces(px.TraceDataset(spans_df.copy()))

    def clean_events_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensures events column contains valid top-level JSON or an empty list for Phoenix compatibility.
        Inner strings that look like JSON are preserved as strings without additional parsing.

        Args:
            df (pd.DataFrame): DataFrame with events column to clean

        Returns:
            pd.DataFrame: DataFrame with cleaned events column

        Note: Consider adding unit tests to verify events column cleaning across different JSON formats.
        """
        if "events" not in df.columns:
            return df

        cleaned_df = df.copy()

        def validate_events_json(events_value):
            # Handle None first
            if events_value is None:
                return []

            # Handle numpy arrays
            if hasattr(events_value, "size") and events_value.size == 0:
                return []

            # Handle pandas/numpy scalars by converting to Python types
            if hasattr(events_value, "item"):
                try:
                    events_value = events_value.item()
                except (ValueError, AttributeError):
                    pass

            # Handle NaN values - convert to bool explicitly
            try:
                if pd.isna(events_value):
                    return []
            except (ValueError, TypeError):
                pass

            # Handle None again after potential conversion
            if events_value is None:
                return []

            # Convert to string for further checks
            events_str = str(events_value)
            if events_str in ["", "nan", "None", "NaN"]:
                return []

            # Handle string values
            if isinstance(events_value, str):
                if events_value.strip() == "":
                    return []
                try:
                    json.loads(events_value)
                    return events_value
                except (json.JSONDecodeError, ValueError):
                    return []

            # Handle list/dict values
            if isinstance(events_value, (list, dict)):
                return events_value

            # Default case
            return []

        cleaned_df["events"] = cleaned_df["events"].apply(validate_events_json)
        return cleaned_df

    def fetch_all_data_bulk(self) -> pd.DataFrame:
        """
        Fetches all span data from Phoenix using get_spans_dataframe with unlimited timeout and max limit.
        Gets all data in a single call without any filters.

        Returns:
            pd.DataFrame: Complete spans dataframe with all available data
        """
        import sys

        spans_df = self.phoenix_client.get_spans_dataframe(
            project_name=self.project_name, limit=sys.maxsize, timeout=None
        )

        return spans_df

    def process_data_bulk(
        self,
        raw_spans_df: pd.DataFrame,
        target_trace_id: Optional[str] = None,
        modify_ids: bool = True,
    ) -> pd.DataFrame:
        """
        Processes raw spans DataFrame into a unified DataFrame ready for Phoenix upload.
        Handles classification of spans including POST calls without parent_id as CHAIN.

        Args:
            raw_spans_df (pd.DataFrame): Raw spans DataFrame from fetch_all_data_bulk()
            target_trace_id (Optional[str]): Specific trace ID to process
            modify_ids (bool): Whether to modify trace_id and span_id for Phoenix upload

        Returns:
            pd.DataFrame: Processed trace data with required columns
        """
        if raw_spans_df.empty:
            return pd.DataFrame()

        processed_df = raw_spans_df.copy()

        # Apply span kind classification logic
        def classify_span_kind(row):
            name = str(row.get("name", "")) if row.get("name") is not None else ""
            parent_id = row.get("parent_id")

            # POST calls without parent_id should be CHAIN
            if "POST" in name and (
                pd.isna(parent_id) or parent_id is None or parent_id == ""
            ):
                return "CHAIN"
            elif name == "Agent.step":
                return "AGENT"
            elif name == "Agent._handle_ai_response":
                # Check if it's a tool or LLM response
                response_message = row.get("parameter.response_message", "")
                if (
                    response_message is not None
                    and not pd.isna(response_message)
                    and isinstance(response_message, str)
                    and response_message.strip()
                ):
                    tool_call, _ = self.parse_response(response_message)
                    if tool_call in ["google_search", "typesense_search"]:
                        return "TOOL"
                    elif tool_call == "send_message":
                        return "LLM"
                return "LLM"  # Default for _handle_ai_response
            elif name == "ToolExecutionSandbox.run_local_dir_sandbox":
                return "CHAIN"
            elif name == "Agent._get_ai_reply":
                return "AGENT"
            else:
                return "CHAIN"  # Default classification

        processed_df["span_kind"] = processed_df.apply(classify_span_kind, axis=1)
        processed_df["attributes.openinference.span.kind"] = processed_df["span_kind"]

        # Filter by target_trace_id if specified
        if target_trace_id:
            processed_df = processed_df[
                processed_df["context.trace_id"] == target_trace_id
            ]

        if processed_df.empty:
            return pd.DataFrame()

        # Modify IDs if requested
        if modify_ids:
            processed_df = self.create_fake_spans(processed_df)

        # Clean events column
        processed_df = self.clean_events_column(processed_df)

        # Sort spans appropriately
        if target_trace_id:
            processed_df = processed_df.sort_values("start_time", ascending=False)
        else:
            processed_df = processed_df.sort_values(
                ["context.trace_id", "start_time"], ascending=[True, False]
            )

        # Clean None values
        processed_df = self.clean_dataframe_nones(processed_df, ["parent_id", "events"])

        return processed_df

    def download_command(self) -> pd.DataFrame:
        """
        Command 1: Download all spans data from Phoenix into memory.

        Returns:
            pd.DataFrame: Raw spans data downloaded from Phoenix
        """
        raw_data = self.fetch_all_data_bulk()
        return raw_data

    def process_command(
        self,
        raw_data: pd.DataFrame,
        target_trace_id: Optional[str] = None,
        modify_ids: bool = True,
    ) -> pd.DataFrame:
        """
        Command 2: Process the downloaded data.

        Args:
            raw_data (pd.DataFrame): Raw data from download_command
            target_trace_id (Optional[str]): Specific trace ID to process
            modify_ids (bool): Whether to modify trace_id and span_id for Phoenix upload

        Returns:
            pd.DataFrame: Processed spans ready for upload
        """
        processed_data = self.process_data_bulk(raw_data, target_trace_id, modify_ids)
        return processed_data

    def upload_command(self, processed_data: pd.DataFrame) -> None:
        """
        Command 3: Upload processed data to Phoenix.

        Args:
            processed_data (pd.DataFrame): Processed data from process_command
        """
        if processed_data.empty:
            return

        self.upload_traces(processed_data)


def main():
    processor = PhoenixTraceProcessor("http://34.60.92.205:6006")

    # Command 1: Download all data into memory
    raw_data = processor.download_command()

    # Command 2: Process the downloaded data
    processed_data = processor.process_command(raw_data, modify_ids=True)

    processed_data = processed_data[
        ~(
            (processed_data["parent_id"].isna())
            & (processed_data["span_kind"] == "CHAIN")
            & (~processed_data["name"].str.startswith("POST"))
        )
    ]
    processor.upload_command(processed_data)


if __name__ == "__main__":
    main()
