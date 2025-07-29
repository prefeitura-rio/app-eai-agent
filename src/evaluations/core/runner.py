import asyncio
from typing import List, Dict, Any

from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import EvaluatedLLMClient
from src.evaluations.core.evals import Evals

class AsyncExperimentRunner:
    """
    Orquestra a execução de um experimento de avaliação de ponta a ponta.
    """

    def __init__(
        self,
        evaluated_client: EvaluatedLLMClient,
        evaluation_suite: Evals,
        metrics_to_run: List[str],
    ):
        """
        Inicializa o Runner.

        Args:
            evaluated_client (EvaluatedLLMClient): O cliente a ser avaliado.
            evaluation_suite (Evals): A suíte de avaliações a ser executada.
            metrics_to_run (List[str]): A lista de nomes das métricas a serem executadas.
        """
        self.evaluated_client = evaluated_client
        self.evaluation_suite = evaluation_suite
        self.metrics_to_run = metrics_to_run

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma única tarefa de ponta a ponta.
        """
        task_id = task.get("id")
        prompt = task.get("prompt")

        if not prompt:
            return {"task_id": task_id, "error": "A tarefa não contém a chave 'prompt'."}

        try:
            # Etapa 1: Executar o cliente principal para obter o resultado
            evaluated_result = await self.evaluated_client.execute(message=prompt)

            # Etapa 2: Executar a suíte de avaliações configurada
            evaluation_results = await self.evaluation_suite.run(
                metrics_to_run=self.metrics_to_run,
                evaluated_result=evaluated_result,
                task=task,
            )

            return {
                "task_id": task_id,
                "original_task": task,
                "evaluated_result": evaluated_result,
                "evaluation_results": evaluation_results,
            }
        except Exception as e:
            return {"task_id": task_id, "error": f"Erro irrecuperável ao processar a tarefa: {e}"}

    async def run(self, loader: DataLoader) -> List[Dict[str, Any]]:
        """
        Executa o experimento completo para todas as tarefas de um DataLoader.
        """
        tasks = list(loader.get_tasks())
        if not tasks:
            print("Nenhuma tarefa para processar.")
            return []

        task_coroutines = [self._process_task(task) for task in tasks]

        results = await tqdm_asyncio.gather(
            *task_coroutines, desc="Executando Experimento de Avaliação"
        )

        return results