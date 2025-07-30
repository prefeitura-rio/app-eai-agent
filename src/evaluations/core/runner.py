import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import logging
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AgentConversationManager
from src.evaluations.core.evals import (
    Evals,
    _EVAL_METHODS_REGISTRY,
    ConversationHandler,
)
from src.services.eai_gateway.api import CreateAgentRequest

logger = logging.getLogger(__name__)


class AsyncExperimentRunner:
    """Orquestra a execução de um experimento, monta o resultado final e o salva."""

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        agent_config: Dict[str, Any],
        evaluation_suite: Evals,
        metrics_to_run: List[str],
        precomputed_responses: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.agent_config = agent_config
        self.evaluation_suite = evaluation_suite
        self.metrics_to_run = metrics_to_run
        self.precomputed_responses = (
            precomputed_responses if precomputed_responses else {}
        )
        if self.precomputed_responses:
            logger.info(
                f"✅ Runner inicializado com {len(self.precomputed_responses)} respostas pré-computadas."
            )
            self._validate_precomputed_responses()

    def _validate_precomputed_responses(self):
        """Valida a estrutura do dicionário de respostas pré-computadas."""
        for task_id, response_data in self.precomputed_responses.items():
            if not isinstance(response_data, dict):
                raise TypeError(
                    f"A resposta para o ID '{task_id}' deve ser um dicionário."
                )
            if (
                "one_turn_output" not in response_data
                and "multi_turn_transcript" not in response_data
            ):
                raise ValueError(
                    f"A resposta para o ID '{task_id}' não contém nem 'one_turn_output' nem 'multi_turn_transcript'."
                )

    async def _get_one_turn_response(
        self, task: Dict[str, Any], agent_config: CreateAgentRequest
    ) -> Dict[str, Any]:
        """Obtém a resposta de turno único, seja de fonte pré-computada ou ao vivo."""
        task_id = task.get("id")
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "one_turn_output" in precomputed_data:
            logger.info(f"↪️ Usando resposta pré-computada para a tarefa {task_id}.")
            return {
                "output": precomputed_data["one_turn_output"],
                "messages": [precomputed_data["one_turn_output"]],
            }

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando resposta ao vivo para a tarefa {task_id}.")
            agent_one = AgentConversationManager(agent_config)
            await agent_one.initialize()
            response = await agent_one.send_message(task.get("prompt"))
            await agent_one.close()
            return response

        return {}

    async def _get_multi_turn_transcript(
        self, task: Dict[str, Any], agent_config: CreateAgentRequest
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Obtém a transcrição multi-turno, seja de fonte pré-computada ou ao vivo."""
        task_id = task.get("id")
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "multi_turn_transcript" in precomputed_data:
            logger.info(f"↪️ Usando transcrição pré-computada para a tarefa {task_id}.")
            transcript = precomputed_data["multi_turn_transcript"]
            last_response = (
                {"output": transcript[-1].get("agent_response")} if transcript else {}
            )
            return transcript, last_response

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando transcrição ao vivo para a tarefa {task_id}.")
            agent_multiple = AgentConversationManager(agent_config)
            await agent_multiple.initialize()
            # Gerenciamento do fechamento da conexão precisa ser feito no _process_task
            handler = ConversationHandler(
                conv_manager=agent_multiple,
                evaluation_suite=self.evaluation_suite,
            )
            return await handler.conduct(task)

        return [], {}

    async def _execute_evaluations(
        self,
        task: Dict[str, Any],
        one_turn_response: Dict[str, Any],
        transcript: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Executa todas as avaliações para uma tarefa e formata os resultados."""
        task_id = task.get("id")
        evaluation_results = []
        coroutine_map = []

        for metric_name in self.metrics_to_run:
            eval_info = _EVAL_METHODS_REGISTRY[metric_name]
            eval_func = getattr(self.evaluation_suite, metric_name)
            error_msg = None

            if eval_info["turns"] == "multiple":
                if transcript:
                    transcript_str = json.dumps(
                        transcript, indent=2, ensure_ascii=False
                    )
                    coroutine_map.append(
                        (
                            metric_name,
                            eval_func(agent_response=transcript_str, task=task),
                        )
                    )
                elif self.precomputed_responses:
                    error_msg = f"Chave 'multi_turn_transcript' não encontrada para a tarefa '{task_id}'"

            else:  # turns == "one"
                if one_turn_response:
                    coroutine_map.append(
                        (
                            metric_name,
                            eval_func(agent_response=one_turn_response, task=task),
                        )
                    )
                elif self.precomputed_responses:
                    error_msg = f"Chave 'one_turn_output' não encontrada para a tarefa '{task_id}'"

            if error_msg:
                logger.warning(
                    f"Erro na avaliação '{metric_name}' para a tarefa '{task_id}': {error_msg}"
                )
                evaluation_results.append(
                    {
                        "eval_name": metric_name,
                        "score": 0.0,
                        "error": True,
                        "error_msg": error_msg,
                        "annotations": None,
                    }
                )

        if coroutine_map:
            gathered_results = await asyncio.gather(
                *[c for _, c in coroutine_map], return_exceptions=True
            )
            valid_metrics = [m for m, _ in coroutine_map]
            for i, res in enumerate(gathered_results):
                metric_name = valid_metrics[i]
                if isinstance(res, Exception):
                    error_msg = f"Exceção durante a avaliação: {str(res)}"
                    logger.error(error_msg)
                    evaluation_results.append(
                        {
                            "eval_name": metric_name,
                            "score": 0.0,
                            "error": True,
                            "error_msg": error_msg,
                            "annotations": None,
                        }
                    )
                else:
                    evaluation_results.append(
                        {
                            "eval_name": metric_name,
                            "score": res.get("score", 0.0),
                            "error": False,
                            "error_msg": None,
                            "annotations": res.get("annotations"),
                        }
                    )

        return sorted(evaluation_results, key=lambda x: x["eval_name"])

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task.get("id")
        logger.info(f"Iniciando processamento da tarefa: {task_id}")

        try:
            agent_config_obj = CreateAgentRequest(**self.agent_config)

            one_turn_response = await self._get_one_turn_response(
                task, agent_config_obj
            )
            transcript, last_response = await self._get_multi_turn_transcript(
                task, agent_config_obj
            )

            evaluation_results = await self._execute_evaluations(
                task, one_turn_response, transcript
            )

            return {
                "task": task,
                "agent_response": {
                    "one": one_turn_response.get("output"),
                    "multiple": last_response.get("output"),
                },
                "reasoning": {
                    "one": one_turn_response.get("messages"),
                    "multiple": transcript,
                },
                "evaluation_results": evaluation_results,
            }
        except Exception as e:
            logger.error(
                f"Erro irrecuperável ao processar a tarefa {task_id}: {e}",
                exc_info=True,
            )
            return {"task": task, "error": f"Erro irrecuperável: {e}"}

    async def run(self, loader: DataLoader):
        tasks = list(loader.get_tasks())
        runs = await tqdm_asyncio.gather(
            *[self._process_task(task) for task in tasks],
            desc=f"Executando: {self.experiment_name}",
        )

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
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados salvos em: {output_path}")
