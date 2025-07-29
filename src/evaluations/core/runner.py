import asyncio
from typing import List, Dict, Any

from tqdm.asyncio import tqdm_asyncio

from .dataloader import DataLoader
from .llm_clients import EvaluatedLLMClient
from .evals import Evaluation

class AsyncExperimentRunner:
    """
    Orquestra a execução de um experimento de avaliação de ponta a ponta.
    """

    def __init__(self, evaluated_client: EvaluatedLLMClient, evaluations: List[Evaluation]):
        """
        Inicializa o Runner.

        Args:
            evaluated_client (EvaluatedLLMClient): O cliente a ser avaliado.
            evaluations (List[Evaluation]): Uma lista de avaliações a serem executadas
                                             no resultado.
        """
        self.evaluated_client = evaluated_client
        self.evaluations = evaluations

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma única tarefa de ponta a ponta.

        1. Executa o cliente a ser avaliado para obter o resultado detalhado.
        2. Executa todas as avaliações em paralelo sobre esse resultado.
        3. Agrega e retorna os resultados.
        """
        task_id = task.get("id")
        prompt = task.get("prompt") # Assumindo que a tarefa tem uma chave 'prompt'

        if not prompt:
            return {"task_id": task_id, "error": "A tarefa não contém a chave 'prompt'."}

        try:
            # Etapa 1: Executar o cliente principal (Serial)
            evaluated_result = await self.evaluated_client.execute(message=prompt)

            # Etapa 2: Executar todas as avaliações (Paralelo)
            evaluation_coroutines = [
                eval.run(evaluated_result, task) for eval in self.evaluations
            ]
            evaluation_results = await asyncio.gather(*evaluation_coroutines, return_exceptions=True)

            # Processa exceções que podem ter ocorrido durante a avaliação
            final_eval_results = []
            for res in evaluation_results:
                if isinstance(res, Exception):
                    final_eval_results.append({"error": f"Exceção na avaliação: {res}"})
                else:
                    final_eval_results.append(res)

            return {
                "task_id": task_id,
                "original_task": task,
                "evaluated_result": evaluated_result,
                "evaluation_results": final_eval_results,
            }
        except Exception as e:
            return {"task_id": task_id, "error": f"Erro irrecuperável ao processar a tarefa: {e}"}

    async def run(self, loader: DataLoader) -> List[Dict[str, Any]]:
        """
        Executa o experimento completo para todas as tarefas de um DataLoader.

        Args:
            loader (DataLoader): O DataLoader que fornece as tarefas.

        Returns:
            List[Dict[str, Any]]: Uma lista de resultados para cada tarefa.
        """
        tasks = list(loader.get_tasks())
        if not tasks:
            print("Nenhuma tarefa para processar.")
            return []

        task_coroutines = [self._process_task(task) for task in tasks]

        results = await tqdm_asyncio.gather(
            *task_coroutines, desc=f"Executando Experimento"
        )

        return results
