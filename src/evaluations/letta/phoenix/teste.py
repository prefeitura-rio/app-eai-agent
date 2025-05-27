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

from src.evaluations.letta.agents.final_response import CLARITY_LLM_JUDGE_PROMPT as ORIGINAL_PROMPT

CLARITY_LLM_JUDGE_PROMPT = """
In this task, you will be presented with a query and an answer. Your objective is to evaluate the clarity 
of the answer in addressing the query. A clear response is one that is precise, coherent, and directly 
addresses the query without introducing unnecessary complexity or ambiguity. An unclear response is one 
that is vague, disorganized, or difficult to understand, even if it may be factually correct.

Your response should be a single word: either "clear" or "unclear," and it should not include any other 
text or characters. "clear" indicates that the answer is well-structured, easy to understand, and 
appropriately addresses the query. "unclear" indicates that some part of the response could be better 
structured or worded.
Please carefully consider the query and answer before determining your response.

After analyzing the query and the answer, you must write a detailed explanation of your reasoning to 
justify why you chose either "clear" or "unclear." Your reasoning should include specific points about how the answer does or does not meet the 
criteria for clarity.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
[END DATA]
Please analyze the data carefully and provide your response.

explanation: 
label: 
"""


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from src.services.llm.gemini_service import gemini_service
from src.config import env

api_key = env.GEMINI_API_KEY

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")
model = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key=api_key)


query_questions = (
    SpanQuery()
    .where(
        "name =='Agent.step'",
    )
    .select(query="parameter.input_messages", trace_id="trace_id")
)

questions = phoenix_client.query_spans(query_questions, project_name="default", timeout=None)

query_tools = (
    SpanQuery()
    .where(
        "name =='Agent._handle_ai_response'",
    )
    .select(tool_call="parameter.response_message", trace_id="trace_id")
)

tool_calls = phoenix_client.query_spans(query_tools, project_name="default", timeout=None)

filter = tool_calls["tool_call"].str.contains("name='google_search'|name='typesense_search'", na=False)
tool_calls = tool_calls[filter]
tool_calls['tool_call'] = tool_calls['tool_call'].str.extract(r'tool_calls=\[(.*)\]')

query_core_memory = SpanQuery().where(
    "name =='ToolExecutionSandbox.run_local_dir_sandbox'",
).select(
    core_memory="parameter.agent_state",
    trace_id="trace_id"
)

core_memory = phoenix_client.query_spans(query_core_memory, project_name="default", timeout=None)

def extrair_valor(texto, label):
    match = re.search(rf"{label}\(value=(?P<quote>['\"])(.*?)(?P=quote)", texto, re.DOTALL)
    if match:
        texto_extraido = match.group(2)
        texto_limpo = texto_extraido.replace('\\n', ' ').strip()  
        texto_limpo = re.sub(' +', ' ', texto_limpo)
        return texto_limpo
    return None

core_memory['persona_value'] = core_memory['core_memory'].apply(lambda x: extrair_valor(x, "Persona"))
core_memory['human_value'] = core_memory['core_memory'].apply(lambda x: extrair_valor(x, "Human"))

core_memory = core_memory.drop('core_memory', axis=1)

query_ai_response = SpanQuery().where(
    "name =='Agent._handle_ai_response'",
).select(
    model_response="parameter.response_message",
    trace_id="trace_id"
)

ai_response = phoenix_client.query_spans(query_ai_response, project_name="default", timeout=None)
ai_response['model_response'] = ai_response['model_response'].str.extract(r'"message":\s*"([^"]+)"')

df_merged = pd.merge(
    questions,
    ai_response.reset_index()[["context.trace_id", "model_response", "context.span_id"]],
    on="context.trace_id",
    how="inner"
)

print("Merged DataFrame columns:", df_merged.columns)
print(df_merged.head())

# Make the context.span_id the index of the DataFrame
df_merged.set_index('context.span_id', inplace=True)

print("DataFrame columns after merging:", df_merged.columns)
print(df_merged.head())

with suppress_tracing():
    clarity_eval = llm_classify(
        data=df_merged,
        template=CLARITY_LLM_JUDGE_PROMPT,
        rails=['clear', 'unclear'],
        model=model,
        provide_explanation=True
    )

clarity_eval['score'] = clarity_eval.apply(lambda x: 1 if x['label'] == 'clear' else 0, axis=1)

print(clarity_eval.head())
print(f"Clarity evaluation columns: {clarity_eval.columns.tolist()}")
print(f"Clarity evaluation index: {clarity_eval.index.tolist()}")

phoenix_client.log_evaluations(
    SpanEvaluations(eval_name="Clarity Eval", dataframe=clarity_eval),
)

# def print_object_structure(obj, prefix="\t", max_depth=3, current_depth=0):
#     if current_depth > max_depth:
#         return
        
#     if hasattr(obj, "__dict__"):
#         for key, value in obj.__dict__.items():
#             print(f"{prefix}{key}: {type(value)}")
#             print_object_structure(value, prefix + "\t", max_depth, current_depth + 1)
#     elif isinstance(obj, dict):
#         for key, value in obj.items():
#             print(f"{prefix}{key}: {type(value)}")
#             print_object_structure(value, prefix + "\t", max_depth, current_depth + 1)
#     elif isinstance(obj, list) and len(obj) > 0:
#         print(f"{prefix}[0]: {type(obj[0])}")
#         print_object_structure(obj[0], prefix + "\t", max_depth, current_depth + 1)


# import asyncio
# async def test_model():
#     try:
#         prompt = "Olá, tudo bem?"
        
#         print("\nTestando chamada direta ao gemini_service:")
#         raw_response = await gemini_service.generate_content(text=prompt, model="gemini-2.5-flash-preview-04-17", response_format="raw")
#         print("Tipo da resposta:", type(raw_response))
#         print("Estrutura da resposta:")
#         print_object_structure(raw_response)
        
#         # Verificar o texto
#         if hasattr(raw_response, "text"):
#             print("Texto da resposta:", raw_response.text)
        
#         print("\nAgora testando pelo modelo:")
#         resposta_teste = await model._async_generate(prompt=prompt)
#         print("Resposta final:", resposta_teste)
        
#     except Exception as e:
#         import traceback
#         print("Erro ao testar o modelo:")
#         print(str(e))
#         print(traceback.format_exc())

# asyncio.run(test_model())

# # print(tool_calls_df.head())