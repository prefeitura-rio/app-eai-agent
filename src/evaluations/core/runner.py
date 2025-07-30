import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AgentConversationManager
from src.evaluations.core.evals import Evals
from src.services.eai_gateway.api import CreateAgentRequest

logger = logging.getLogger(__name__)


class AsyncExperimentRunner:
    """
    Orquestra a execução de um experimento, monta o resultado final e o salva.
    """

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        evaluation_suite: Evals,
        metrics_to_run: List[str],
    ):
        """
        Inicializa o Runner.

        Args:
            experiment_name (str): Nome do experimento.
            experiment_description (str): Descrição do experimento.
            metadata (Dict[str, Any]): Metadados da execução (config do agente).
            evaluation_suite (Evals): A suíte de avaliações a ser executada.
            metrics_to_run (List[str]): A lista de nomes das métricas a serem executadas.
        """
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.evaluation_suite = evaluation_suite
        self.metrics_to_run = metrics_to_run

    async def _process_task(
        self, task: Dict[str, Any], conversation_manager: AgentConversationManager
    ) -> Dict[str, Any]:
        """Processa uma única tarefa."""
        task_id = task.get("id")
        logger.info(f"Iniciando processamento da tarefa: {task_id}")

        if not task.get("prompt"):
            error_msg = "A tarefa não contém a chave 'prompt' padronizada."
            logger.error(f"Erro na tarefa {task_id}: {error_msg}")
            return {"task": task, "error": error_msg}

        try:
            # Etapa 2: Executa a suíte de avaliações
            logger.info(f"Executando suíte de avaliações para a tarefa: {task_id}")
            evaluation_results_with_responses = await self.evaluation_suite.run(
                metrics_to_run=self.metrics_to_run,
                conversation_manager=conversation_manager,
                task=task,
            )
            logger.info(f"Suíte de avaliações concluída para a tarefa: {task_id}")

            # Extrai a última resposta do agente do primeiro resultado (é a mesma para todos)
            last_agent_response = {}
            if evaluation_results_with_responses:
                last_agent_response = evaluation_results_with_responses[0].get(
                    "last_agent_response", {}
                )

            # Limpa a chave 'last_agent_response' dos resultados para evitar duplicação
            evaluation_results_cleaned = []
            for res in evaluation_results_with_responses:
                cleaned_res = {
                    "eval_name": res.get("eval_name"),
                    "score": res.get("score"),
                    "annotations": res.get("annotations"),
                }
                evaluation_results_cleaned.append(cleaned_res)

            return {
                "task": task,
                "agent_response": last_agent_response.get("output"),
                "agent_response_raw": last_agent_response,
                "evaluation_results": evaluation_results_cleaned,
            }
        except Exception as e:
            logger.error(
                f"Erro irrecuperável ao processar a tarefa {task_id}: {e}",
                exc_info=True,
            )
            return {
                "task": task,
                "error": f"Erro irrecuperável ao processar a tarefa: {e}",
            }

    async def run(self, loader: DataLoader):
        """
        Executa o experimento completo, monta o resultado e salva em arquivo.
        """
        tasks = list(loader.get_tasks())
        if not tasks:
            logger.warning("Nenhuma tarefa para processar.")
            return

        logger.info(f"Iniciando execução do experimento para {len(tasks)} tarefa(s).")
        
        # Recria o objeto Pydantic a partir do dicionário de metadados
        agent_config_obj = CreateAgentRequest(**self.metadata)
        
        # O ConversationManager é criado uma vez para o experimento
        conversation_manager = AgentConversationManager(agent_config_obj)
        await conversation_manager.initialize()

        try:
            task_coroutines = [
                self._process_task(task, conversation_manager) for task in tasks
            ]
            runs = await tqdm_asyncio.gather(
                *task_coroutines, desc=f"Executando Experimento: {self.experiment_name}"
            )
        finally:
            await conversation_manager.close()
            logger.info("Conversa com o agente para o experimento encerrada.")

        logger.info("Montando o JSON de resultado final.")
        final_result = {
            **loader.get_dataset_config(),
            "experiment_id": f"exp_{uuid.uuid4()}",
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
            "runs": runs,
        }

        output_dir = "evaluation_results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"results_{self.experiment_name}.json")

        logger.info(f"Salvando resultados em: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)

        logger.info("Execução do experimento concluída com sucesso.")
