import sys
import os
import time
import asyncio
import logging
from functools import partial
from typing import Dict, List, Any, Callable, Coroutine, Optional, Tuple
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

try:
    from src.config import env
    from src.evaluations.letta.phoenix.training_dataset.evaluators import *
    from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
    from src.services.letta.agents.memory_blocks.agentic_search_mb import get_agentic_search_memory_blocks

    os.environ["PHOENIX_HOST"] = os.getenv("PHOENIX_HOST", env.PHOENIX_HOST)
    os.environ["PHOENIX_PORT"] = os.getenv("PHOENIX_PORT", env.PHOENIX_PORT)
    os.environ["PHOENIX_ENDPOINT"] = os.getenv("PHOENIX_ENDPOINT", env.PHOENIX_ENDPOINT)

    import pandas as pd
    import httpx
    import phoenix as px
    import nest_asyncio
    nest_asyncio.apply()

    from phoenix.evals import llm_classify
    from phoenix.experiments.types import Example
    from phoenix.experiments import run_experiment
except ImportError as e:
    logger.error(f"Erro de importação: {e}")
    raise
except EnvironmentError as e:
    logger.error(f"Erro de variável de ambiente: {e}")
    logger.info("Defina as variáveis de ambiente necessárias em um arquivo .env")
    sys.exit(1)

try:
    phoenix_client = px.Client(endpoint=os.getenv("PHOENIX_ENDPOINT", env.PHOENIX_ENDPOINT))
    EVAL_MODEL = GenAIModel(
        model="gemini-2.5-flash-preview-04-17", 
        api_key=os.getenv("GEMINI_API_KEY", env.GEMINI_API_KEY)
    )
except Exception as e:
    logger.error(f"Erro ao inicializar clientes ou modelos: {e}")
    phoenix_client = None
    EVAL_MODEL = None


async def get_response_from_letta(input_data):
    """Obtém a resposta do agente LETTA de forma assíncrona"""
    await asyncio.sleep(30)
    
    if isinstance(input_data, dict):
        pergunta = input_data.get("pergunta", "")
    else:
        pergunta = str(input_data)
    
    url = f"{os.getenv('EAI_AGENT_URL', env.EAI_AGENT_URL)}letta/test-message-raw"
    payload = {
        "agent_id": "agent-45d877fa-4f50-4935-a18f-8a481291c950",
        "message": pergunta,
        "name": "Usuário Teste",
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('EAI_AGENT_TOKEN', env.EAI_AGENT_TOKEN)}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=500) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if not data:
                raise RuntimeError("Resposta vazia do agente.")
            return data
        
    except httpx.HTTPStatusError as exc:
        logger.error(f"Erro na chamada para Letta: {exc.response.status_code} - {exc.response.text}")
        raise RuntimeError(f"Erro na chamada para Letta: {exc.response.status_code} - {exc.response.text}") from exc
    except Exception as e:
        logger.error(f"Erro ao processar resposta do agente: {str(e)}")
        raise


def final_response(agent_stream: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai a resposta final do stream do agente"""
    if not agent_stream or "assistant_messages" not in agent_stream:
        return {}
    
    if not agent_stream["assistant_messages"]:
        return {}
        
    return agent_stream["assistant_messages"][-1]


def tool_returns(agent_stream: Dict[str, Any]) -> str:
    """Formata os retornos das ferramentas em formato de texto"""
    if not agent_stream:
        return ""
     
    returns = [
        f"Tool Return {i + 1}:\n"
        f"Tool Name: {msg.get('name', 'Unknown')}\n"
        f"Tool Result: {msg.get('tool_return', '').strip()}\n"
        for i, msg in enumerate(agent_stream.get("tool_return_messages", []))
    ]
    
    return "\n".join(returns)


def search_tool_returns_summary(agent_stream: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extrai um resumo dos resultados das ferramentas de busca"""
    if not agent_stream:
        return []
    
    search_tool_returns = [
        {
            "title": msg.get('tool_return', {}).get('title', ''),
            "summary": msg.get('tool_return', {}).get('summary', '')
        }
        for msg in agent_stream.get("tool_return_messages", [])
        if msg.get('name') == 'search_tool'
    ]

    return search_tool_returns


def empty_agent_core_memory() -> str:
    """Retorna a memória base do agente em formato de texto"""
    core_memory = [f"{mb['label']}: {mb['value']}" for mb in get_agentic_search_memory_blocks()]

    return "\n".join(core_memory)


async def experiment_eval(input: Dict[str, Any], output: Dict[str, Any], prompt: str, 
                   rails: List[str], expected: Optional[Dict[str, Any]] = None, 
                   **kwargs) -> Tuple[bool, str]:
    """Avalia a resposta do modelo usando o LLM"""
    if not output:
        return False, "Sem saída do modelo para avaliar"
    
    try:
        df = pd.DataFrame({
            "query": [input.get("pergunta", "")], 
            "model_response": [final_response(output).get("content", "")],
        })
        
        if expected:
            df["ideal_response"] = [expected.get("resposta_ideal", "")]

        for k, val in kwargs.items():
            if isinstance(val, str):
                df[k] = [val]
            elif isinstance(val, list):
                df[k] = [", ".join(val)]
            else:
                df[k] = [val]

        try:
            response = llm_classify(
                data=df,
                template=prompt,
                rails=rails,
                model=EVAL_MODEL,
                provide_explanation=True
            )
            
            if isinstance(response, dict):
                eval_result = response.get('label') == rails[0]
                explanation = response.get("explanation", "")
            elif isinstance(response, list) and len(response) > 0:
                if isinstance(response[0], dict):
                    eval_result = response[0].get('label') == rails[0]
                    explanation = response[0].get("explanation", "")
                else:
                    eval_result = response[0] == rails[0]
                    explanation = "Sem explicação disponível"
            else:
                eval_result = False
                explanation = f"Formato de resposta inesperado: {str(response)}"
                
            return (eval_result, explanation)
            
        except Exception as e:
            logger.error(f"Erro na chamada de llm_classify: {str(e)}")
            return (False, f"Erro na classificação LLM: {str(e)}")
    
    except Exception as e:
        logger.error(f"Erro na avaliação: {str(e)}")
        return (False, f"Erro na avaliação: {str(e)}")


async def run_async_experiment(dataset, evaluator_functions):
    """Executa o experimento de forma assíncrona"""
    results = []
    
    if hasattr(dataset, 'examples'):
        examples = dataset.examples
    else:
        examples = dataset
        
    total = len(examples)
    
    logger.info(f"Iniciando processamento de {total} exemplos")

    evaluator_names = {
        "experiment_eval_answer_completeness": "answer_completeness",
        "experiment_eval_groundedness": "groundedness",
        "experiment_eval_search_result_coverage": "search_result_coverage",
        "experiment_eval_clarity": "clarity",
        "experiment_eval_gold_standard_similarity": "gold_standard_similarity",
        "experiment_eval_entity_presence": "entity_presence",
        "experiment_eval_feedback_handling_compliance": "feedback_handling_compliance",
        "experiment_eval_emergency_handling_compliance": "emergency_handling_compliance",
        "experiment_eval_location_policy_compliance": "location_policy_compliance",
        "experiment_eval_security_privacy_compliance": "security_privacy_compliance",
        "experiment_eval_whatsapp_formatting_compliance": "whatsapp_formatting_compliance",
        "experiment_eval_tool_calling": "tool_calling",
        "experiment_eval_search_query_effectiveness": "search_query_effectiveness"
    }
    
    for i, example in enumerate(examples):
        try:
            example_id = getattr(example, 'id', None)
            if example_id is None and isinstance(example, dict):
                example_id = example.get('id', f"exemplo_{i}")
            elif example_id is None:
                example_id = f"exemplo_{i}"
                
            logger.info(f"Processando exemplo {i+1}/{total}: {example_id}")
            
            if hasattr(example, 'input'):
                input_data = example.input
            elif isinstance(example, dict):
                input_data = example.get('input', {})
            else:
                input_data = {'pergunta': str(example)}
                
            if hasattr(example, 'expected'):
                expected_data = example.expected
            elif isinstance(example, dict):
                expected_data = example.get('expected', {})
            else:
                expected_data = {}
            
            if not isinstance(input_data, dict):
                input_data = {'pergunta': str(input_data)}
            elif 'pergunta' not in input_data:
                input_data['pergunta'] = next(iter(input_data.values())) if input_data else ""
            
            try:
                response = await get_response_from_letta(input_data)
                
                if not response:
                    logger.warning(f"Resposta vazia do agente para exemplo {i+1}")
                    response = {}
            except Exception as agent_error:
                logger.error(f"Erro ao obter resposta do agente: {str(agent_error)}")
                response = {}
            
            example_results = {}
            for evaluator in evaluator_functions:
                if hasattr(evaluator, '__name__'):
                    eval_name = evaluator_names.get(evaluator.__name__, evaluator.__name__.replace("experiment_eval_", ""))
                elif hasattr(evaluator, 'name'):
                    eval_name = evaluator.name
                elif hasattr(evaluator, '__class__'):
                    eval_name = evaluator.__class__.__name__
                else:
                    eval_name = f"evaluator_{id(evaluator)}"
                
                logger.info(f"  Executando avaliador: {eval_name}")
                
                try:
                    eval_result, explanation = await evaluator(
                        input=input_data,
                        output=response,
                        expected=expected_data
                    )
                    example_results[eval_name] = {
                        "result": eval_result,
                        "explanation": explanation
                    }
                except Exception as eval_error:
                    logger.error(f"  Erro no avaliador {eval_name}: {str(eval_error)}")
                    example_results[eval_name] = {
                        "result": False,
                        "explanation": f"Erro: {str(eval_error)}"
                    }
            
            pergunta = input_data.get('pergunta', '')
            if not pergunta and isinstance(input_data, str):
                pergunta = input_data
                
            results.append({
                "example_id": example_id,
                "query": pergunta,
                "response": final_response(response).get("content", ""),
                "evaluations": example_results
            })
            
            logger.info(f"Exemplo {i+1}/{total} processado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao processar exemplo {i+1}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            example_id = getattr(example, 'id', f"exemplo_{i}") if hasattr(example, 'id') else f"exemplo_{i}"
            pergunta = ""
            
            if hasattr(example, 'input'):
                pergunta = example.input.get('pergunta', '') if isinstance(example.input, dict) else str(example.input)
            elif isinstance(example, dict):
                pergunta = example.get('input', {}).get('pergunta', '') if isinstance(example.get('input'), dict) else str(example.get('input', ''))
            else:
                pergunta = str(example)
                
            results.append({
                "example_id": example_id,
                "query": pergunta,
                "error": str(e),
                "evaluations": {}
            })
    
    return results


async def save_results(results, filename="experiment_results.json"):
    """Salva os resultados do experimento em um arquivo JSON"""
    import json
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Resultados salvos em {filename}")
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {str(e)}")


async def main():
    """Função principal do script"""
    logger.info("Iniciando a execução do script...")

    try:
        dataset_name = os.getenv("DATASET_NAME", "Typesense_IA_Dataset-2025-06-04")
        
        if not phoenix_client:
            logger.error("Cliente Phoenix não inicializado. Verifique as variáveis de ambiente.")
            return

        try:
            dataset = phoenix_client.get_dataset(name=dataset_name)
            if not dataset or not dataset.examples:
                logger.error(f"Dataset '{dataset_name}' não encontrado ou vazio")
                return
                
            logger.info(f"Dataset '{dataset_name}' carregado com {len(dataset.examples)} exemplos")
        except Exception as e:
            logger.error(f"Erro ao carregar dataset: {str(e)}")
            return
        
        from src.evaluations.letta.phoenix.training_dataset.evaluators import (
            experiment_eval_answer_completeness,
            experiment_eval_groundedness,
            experiment_eval_search_result_coverage,
        )
        
        async_evaluators = [
            experiment_eval_answer_completeness,
            experiment_eval_groundedness,
            experiment_eval_search_result_coverage,
        ]
        
        evaluator_names = ["answer_completeness", "groundedness", "search_result_coverage"]
        
        logger.info(f"Executando experimento com o dataset: {dataset_name}")
        results = await run_async_experiment(dataset, async_evaluators)
        
        await save_results(results)
        
        logger.info(f"Experimento concluído. Processados {len(results)} exemplos.")
        
        total_examples = len(results)
        success_by_eval = {}
        
        for eval_name in evaluator_names:
            success_count = sum(1 for r in results if r.get("evaluations", {}).get(eval_name, {}).get("result", False))
            success_rate = success_count / total_examples if total_examples > 0 else 0
            success_by_eval[eval_name] = {
                "success_count": success_count,
                "success_rate": success_rate
            }
        
        logger.info("\nResultados por avaliador:")
        for eval_name, stats in success_by_eval.items():
            logger.info(f"{eval_name}: {stats['success_count']}/{total_examples} ({stats['success_rate']*100:.2f}%)")
            
    except Exception as e:
        logger.error(f"Erro na execução do experimento: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Experimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
