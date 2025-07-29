import asyncio
import json
from typing import Dict, Any, List, Union, Callable, Awaitable

# Importa os clientes que serão usados como Juízes
from src.evaluations.core.llm_clients import AzureOpenAIClient, GeminiAIClient
# Importa os templates de prompt centralizados
from src.evaluations.core import prompt_judges

# --- Dicionário de Registro para Métodos de Avaliação ---
# Este dicionário será preenchido pelo decorador @eval_method
_EVAL_METHODS_REGISTRY: Dict[str, Callable] = {}

def eval_method(name: str) -> Callable:
    """
    Decorador para registrar um método de avaliação no _EVAL_METHODS_REGISTRY.
    """
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable:
        _EVAL_METHODS_REGISTRY[name] = func
        return func
    return decorator

class Evals:
    """
    Uma classe unificada para executar uma suíte de avaliações,
    reutilizando uma única instância de um cliente LLM (Juiz).
    """
    def __init__(self, judge_client: Union[AzureOpenAIClient, GeminiAIClient]):
        """
        Args:
            judge_client (Union[AzureOpenAIClient, GeminiAIClient]):
                A instância do cliente LLM a ser usada para todas as avaliações de juiz.
        """
        self.judge_client = judge_client

    @eval_method(name="semantic_correctness")
    async def evaluate_semantic_correctness(self, result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia a correção semântica usando um Juiz LLM."""
        prompt = prompt_judges.SEMANTIC_CORRECTNESS_PROMPT.format(
            output=result.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        try:
            return json.loads(judgement_response)
        except (json.JSONDecodeError, TypeError):
            return {"raw_response": judgement_response}

    @eval_method(name="persona_adherence")
    async def evaluate_persona_adherence(self, result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia a aderência à persona usando um Juiz LLM."""
        prompt = prompt_judges.PERSONA_ADHERENCE_PROMPT.format(
            output=result.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        try:
            return json.loads(judgement_response)
        except (json.JSONDecodeError, TypeError):
            return {"raw_response": judgement_response}

    @eval_method(name="keyword_match")
    async def check_keyword_match(self, result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia se a resposta final contém uma palavra-chave da tarefa."""
        keywords = task.get("keywords", [])
        final_answer = result.get("output", "").lower()
        found = [kw for kw in keywords if kw.lower() in final_answer]
        return {"score": 1.0 if found else 0.0, "found_keywords": found}

    async def run(self, metrics_to_run: List[str], evaluated_result: Dict[str, Any], task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa uma lista de avaliações especificadas por nome, em paralelo.
        """
        coroutines: List[Awaitable] = []
        for metric_name in metrics_to_run:
            eval_func = _EVAL_METHODS_REGISTRY.get(metric_name)
            if eval_func:
                # self é passado para vincular o método à instância
                coroutines.append(eval_func(self, evaluated_result, task))
        
        if not coroutines:
            return []

        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        final_results = []
        # Mapeia os resultados de volta para os nomes das métricas
        for i, metric_name in enumerate(metrics_to_run):
            if i < len(results):
                res = results[i]
                if isinstance(res, Exception):
                    final_results.append({"eval_name": metric_name, "error": str(res)})
                else:
                    final_results.append({"eval_name": metric_name, "result": res})
        return final_results

# --- Bloco de Exemplo ---
async def main():
    """Função de exemplo para demonstrar a nova arquitetura."""
    
    azure_judge = AzureOpenAIClient(model_name="gpt-4o")
    evaluation_suite = Evals(judge_client=azure_judge)

    metrics = ["semantic_correctness", "keyword_match", "non_existent_eval"]

    sample_task = {
        "id": 1,
        "prompt": "Quem é você?",
        "golden_response": "Eu sou o Batman.",
        "keywords": ["Batman"]
    }
    sample_result = {"output": "Eu sou o Batman."}

    results = await evaluation_suite.run(
        metrics_to_run=metrics,
        evaluated_result=sample_result,
        task=sample_task
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())