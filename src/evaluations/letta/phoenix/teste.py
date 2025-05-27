import os
import re
import pandas as pd
import phoenix as px

from phoenix.evals import llm_classify
from phoenix.trace.dsl import SpanQuery
from llm_models.genai_model import GenAIModel
from google.oauth2 import service_account
from phoenix.trace import SpanEvaluations

from openinference.instrumentation import suppress_tracing

from src.evaluations.letta.agents.final_response import CLARITY_LLM_JUDGE_PROMPT


import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)
from src.config import env

api_key = env.GEMINI_API_KEY

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")
model = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key=api_key)

def extrair_valor(texto, label):
    match = re.search(
        rf"{label}\(value=(?P<quote>['\"])(.*?)(?P=quote)", texto, re.DOTALL
    )
    if match:
        texto_extraido = match.group(2)
        texto_limpo = texto_extraido.replace("\\n", " ").strip()
        texto_limpo = re.sub(" +", " ", texto_limpo)
        return texto_limpo
    return None

def parse_response(response):
    tool = re.search(r'tool_calls=\[(.*?)\]', response)
    tool = tool.group(1) if tool else None

    if tool and "send_message" in tool:
      message = re.search(r"arguments='\{(.*)\}'", tool, re.DOTALL).group(1)
      message = re.sub(r'\s*"request_heartbeat":\s*(true|false)\s*,?', '', message).strip()
      message = re.sub(r'^(\\n|\s)+|(\s|\\n)+$', '', message)
    else:
      message = None

    return tool, message


query_questions = (
    SpanQuery()
    .where(
        "name =='Agent.step'",
    )
    .select(query="parameter.input_messages", trace_id="trace_id")
)

questions = phoenix_client.query_spans(
    query_questions, project_name="default", timeout=None
)

query_response = (
    SpanQuery()
    .where(
        "name =='Agent._handle_ai_response'",
    )
    .select(response_message="parameter.response_message", trace_id="trace_id")
)

response_message = phoenix_client.query_spans(query_response, project_name="default", timeout=None)

response_message[["tool", "model_response"]] = response_message["response_message"].apply(lambda x: pd.Series(parse_response(x)))

model_response = response_message[(response_message["tool"] == 'send_message')]
tools = response_message[(response_message["tool"] == 'google_search') | (response_message["tool"] == 'typesense_search')]

query_core_memory = (
    SpanQuery()
    .where(
        "name =='ToolExecutionSandbox.run_local_dir_sandbox'",
    )
    .select(core_memory="parameter.agent_state", trace_id="trace_id")
)

core_memory = phoenix_client.query_spans(
    query_core_memory, project_name="default", timeout=None
)


core_memory["persona_value"] = core_memory["core_memory"].apply(
    lambda x: extrair_valor(x, "Persona")
)
core_memory["human_value"] = core_memory["core_memory"].apply(
    lambda x: extrair_valor(x, "Human")
)

core_memory = core_memory.drop("core_memory", axis=1)

df_merged = pd.merge(
    questions,
    model_response.reset_index()[
        ["context.trace_id", "model_response", "context.span_id"]
    ],
    on="context.trace_id",
    how="inner",
)

print("Merged DataFrame columns:", df_merged.columns)
print(df_merged.head())

# Make the context.span_id the index of the DataFrame
df_merged.set_index("context.span_id", inplace=True)

print("DataFrame columns after merging:", df_merged.columns)
print(df_merged.head())

# with suppress_tracing():
#     clarity_eval = llm_classify(
#         data=df_merged,
#         template=CLARITY_LLM_JUDGE_PROMPT,
#         rails=["clear", "unclear"],
#         model=model,
#         provide_explanation=True,
#     )

# clarity_eval["score"] = clarity_eval.apply(
#     lambda x: 1 if x["label"] == "clear" else 0, axis=1
# )

# print(clarity_eval.head())
# print(f"Clarity evaluation columns: {clarity_eval.columns.tolist()}")
# print(f"Clarity evaluation index: {clarity_eval.index.tolist()}")

# phoenix_client.log_evaluations(
#     SpanEvaluations(eval_name="Clarity Eval", dataframe=clarity_eval),
# )
