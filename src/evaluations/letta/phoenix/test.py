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

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")

tool_definitions = get_system_prompt()
tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

query_questions = (
    SpanQuery()
    .where(
        "name =='Agent.step'",
    )
    .select(query="parameter.input_messages", trace_id="trace_id")
)

questions = phoenix_client.query_spans(query_questions, project_name="default", timeout=None)

questions["query"] = questions["query"].apply(extrair_content)

query_response = (
    SpanQuery()
    .where(
        "name =='Agent._handle_ai_response'",
    )
    .select(response_message="parameter.response_message", trace_id="trace_id")
)

response_message = phoenix_client.query_spans(query_response, project_name="default", timeout=None)

response_message[["tool_call", "model_response"]] = response_message["response_message"].apply(lambda x: pd.Series(parse_response(x)))

model_response = response_message[(response_message["tool_call"] == "send_message")]
tools = response_message[(response_message["tool_call"] == "google_search") | (response_message["tool_call"] == "typesense_search")]

tools["search_tool_query"] = tools["response_message"].apply(extrair_query)

query_core_memory = (
    SpanQuery()
    .where(
        "name =='ToolExecutionSandbox.run_local_dir_sandbox'",
    )
    .select(core_memory="parameter.agent_state", trace_id="trace_id")
)

core_memory = phoenix_client.query_spans(query_core_memory, project_name="default", timeout=None)

core_memory["persona_value"] = core_memory["core_memory"].apply(lambda x: extrair_valor(x, "Persona"))
core_memory["human_value"] = core_memory["core_memory"].apply(lambda x: extrair_valor(x, "Human"))

core_memory = core_memory.drop("core_memory", axis=1)


def main(df1, df2, column):
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


if __name__ == "__main__":
    df = main(questions, model_response, "model_response")
    rails_clarity = ["clear", "unclear"]
    eval(df, CLARITY_LLM_JUDGE_PROMPT, rails_clarity, "Clarity Eval")

    df = main(questions, tools, "tool_call")
    rails_tool_calling = ["correct", "incorrect"]
    template = TOOL_CALLING_LLM_JUDGE_PROMPT.replace("{tool_definitions}", tool_definitions)
    eval(df, template, rails_tool_calling, "Tool Calling")

    df = main(questions, tools, "search_tool_query")
    rails_search_query_eff = ["effective", "innefective"]
    eval(df, SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT, rails_search_query_eff, "Search Query Effectiveness")

    df = main(questions, model_response, "model_response")
    rails_entity_presence = ["entities_present", "entities_missing"]
    eval(df, ENTITY_PRESENCE_LLM_JUDGE_PROMPT, rails_entity_presence, "Entity Presence")

    df = main(questions, model_response, "model_response")
    rails_answer_completeness = ["answered", "unanswered"]
    eval(df, ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT, rails_answer_completeness, "Answer Completeness")

    df = main(questions, model_response, "model_response")
    rails_security_privacy_compliance = ["compliant", "non_compliant"]
    eval(df, SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT, rails_security_privacy_compliance, "Security Privacy Compliance")

    df = main(questions, model_response, "model_response")
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]
    eval(df, FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT, rails_feedback_handling_compliance, "Feedback Handling Compliance")

    df = main(questions, model_response, "model_response")
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]
    eval(df, EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT, rails_emergency_handling_compliance, "Emergency Handling Compliance")

    df = main(questions, model_response, "model_response")
    rails_location_policy_compliance = ["compliant", "non_compliant"]
    eval(df, LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT, rails_location_policy_compliance, "Location Policy Compliance")
