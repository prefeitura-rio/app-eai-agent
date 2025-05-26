import phoenix as px
from phoenix.evals import (
    TOOL_CALLING_PROMPT_TEMPLATE, 
    llm_classify,
    GeminiModel
)
from llm_models.genai_model import GenAIModel
from google.oauth2 import service_account
from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from src.services.llm.gemini_service import gemini_service

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")

query = SpanQuery().where(
    # Filter for the `LLM` span kind.
    # The filter condition is a string of valid Python boolean expression.
    "name =='Agent.step'",
).select(
    question="parameter.input_messages",
)

tool_calls_df = phoenix_client.query_spans(query, 
                                        project_name="default", 
                                        timeout=None)

tool_calls_df = tool_calls_df.dropna(subset=["tool_call"])



model = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key="")

def print_object_structure(obj, prefix="\t", max_depth=3, current_depth=0):
    if current_depth > max_depth:
        return
        
    if hasattr(obj, "__dict__"):
        for key, value in obj.__dict__.items():
            print(f"{prefix}{key}: {type(value)}")
            print_object_structure(value, prefix + "\t", max_depth, current_depth + 1)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{prefix}{key}: {type(value)}")
            print_object_structure(value, prefix + "\t", max_depth, current_depth + 1)
    elif isinstance(obj, list) and len(obj) > 0:
        print(f"{prefix}[0]: {type(obj[0])}")
        print_object_structure(obj[0], prefix + "\t", max_depth, current_depth + 1)


import asyncio
async def test_model():
    try:
        prompt = "Olá, tudo bem?"
        
        print("\nTestando chamada direta ao gemini_service:")
        raw_response = await gemini_service.generate_content(text=prompt, model="gemini-2.5-flash-preview-04-17", response_format="raw")
        print("Tipo da resposta:", type(raw_response))
        print("Estrutura da resposta:")
        print_object_structure(raw_response)
        
        # Verificar o texto
        if hasattr(raw_response, "text"):
            print("Texto da resposta:", raw_response.text)
        
        print("\nAgora testando pelo modelo:")
        resposta_teste = await model._async_generate(prompt=prompt)
        print("Resposta final:", resposta_teste)
        
    except Exception as e:
        import traceback
        print("Erro ao testar o modelo:")
        print(str(e))
        print(traceback.format_exc())

asyncio.run(test_model())

# print(tool_calls_df.head())