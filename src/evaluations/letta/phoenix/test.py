import os
import sys
import json

import pandas as pd
import phoenix as px
from phoenix.trace.dsl import SpanQuery

from src.evaluations.letta.agents.final_response import (
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    CLARITY_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.router import (
    SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
    TOOL_CALLING_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.phoenix.utils import (
    extrair_content,
    extrair_query,
    extrair_valor,
    get_system_prompt,
    parse_response,
    eval,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")


def fetch_questions() -> pd.DataFrame:
    query = (
        SpanQuery()
        .where("name =='Agent.step'")
        .select(query="parameter.input_messages", trace_id="trace_id")
    )
    df = phoenix_client.query_spans(query, project_name="default", timeout=None)
    df["query"] = df["query"].apply(extrair_content)

    return df


def fetch_responses() -> tuple[pd.DataFrame, pd.DataFrame]:
    query = (
        SpanQuery()
        .where("name =='Agent._handle_ai_response'")
        .select(response_message="parameter.response_message", trace_id="trace_id")
    )

    df = phoenix_client.query_spans(query, project_name="default", timeout=None)
    df[["tool_call", "model_response"]] = df["response_message"].apply(lambda x: pd.Series(parse_response(x)))

    model_response = df[(df["tool_call"] == "send_message")]
    tools = df[df["tool_call"].isin(["google_search", "typesense_search"])]
    tools["search_tool_query"] = tools["response_message"].apply(extrair_query)

    return model_response, tools


def fetch_core_memory() -> pd.DataFrame:
    query = (
        SpanQuery()
        .where("name =='ToolExecutionSandbox.run_local_dir_sandbox'")
        .select(core_memory="parameter.agent_state", trace_id="trace_id")
    )

    df = phoenix_client.query_spans(query, project_name="default", timeout=None)
    df["persona_value"] = df["core_memory"].apply(lambda x: extrair_valor(x, "Persona"))
    df["human_value"] = df["core_memory"].apply(lambda x: extrair_valor(x, "Human"))

    return df.drop(columns=["core_memory"])


def merge_by_trace(df1: pd.DataFrame, df2: pd.DataFrame, column: str) -> pd.DataFrame:
    df_merged = pd.merge(
        df1,
        df2.reset_index()[["context.trace_id", "context.span_id", column]],
        on="context.trace_id",
        how="inner",
    )

    df_merged.set_index("context.span_id", inplace=True)

    return df_merged


def test_ideal_response():
    with open("file.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    print(df)

def run_eval(df1: pd.DataFrame, df2: pd.DataFrame, column: str, prompt: str, rails: list[str], name: str):
    df = merge_by_trace(df1, df2, column)
    eval(df, prompt, rails, name)


if __name__ == "__main__":
    tool_definitions = get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

    questions = fetch_questions()
    model_response, tools = fetch_responses()
    core_memory = fetch_core_memory()

    rails_clarity = ["clear", "unclear"]
    rails_tool_calling = ["correct", "incorrect"]
    rails_search_query_effectiveness = ["effective", "innefective"]
    rails_entity_presence = ["entities_present", "entities_missing"]
    rails_answer_completeness = ["answered", "unanswered"]
    rails_security_privacy = ["compliant", "non_compliant"]
    rails_feedback_handling = ["compliant", "non_compliant"]
    rails_emergency_handling = ["compliant", "non_compliant"]
    rails_location_policy = ["compliant", "non_compliant"]
    rails_whatsapp_formatting = ["compliant_format", "non_compliant_format"]

    # Clarity
    run_eval(questions, model_response, "model_response", CLARITY_LLM_JUDGE_PROMPT, rails_clarity, "Clarity Eval")

    # Tool Calling
    tool_prompt = TOOL_CALLING_LLM_JUDGE_PROMPT.replace("{tool_definitions}", tool_definitions)
    run_eval(questions, tools, "tool_call", tool_prompt, rails_tool_calling, "Tool Calling")

    # Search Query Effectiveness
    run_eval(questions, tools, "search_tool_query", SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT, rails_search_query_effectiveness, "Search Query Effectiveness")

    # Entity Presence
    run_eval(questions, model_response, "model_response", ENTITY_PRESENCE_LLM_JUDGE_PROMPT, rails_entity_presence, "Entity Presence")

    # Answer Completeness
    run_eval(questions, model_response, "model_response", ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT, rails_answer_completeness, "Answer Completeness")

    # Security and Privacy
    run_eval(questions, model_response, "model_response", SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT, rails_security_privacy, "Security Privacy Compliance")

    # Feedback Handling
    run_eval(questions, model_response, "model_response", FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT, rails_feedback_handling, "Feedback Handling Compliance")

    # Emergency Handling
    run_eval(questions, model_response, "model_response", EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT, rails_emergency_handling, "Emergency Handling Compliance")

    # Location Policy
    run_eval(questions, model_response, "model_response", LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT, rails_location_policy, "Location Policy Compliance")

    # WhatsApp Formatting Compliance
    run_eval(questions, model_response, "model_response", WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT, rails_whatsapp_formatting, "WhatsApp Formatting Compliance")
