# -*- coding: utf-8 -*-
import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from pydantic import BaseModel, ValidationError
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.eval.dataloader import DataLoader
from src.evaluations.core.eval.evaluators.base import (
    BaseEvaluator,
    BaseConversationEvaluator,
    BaseOneTurnEvaluator,
    BaseMultipleTurnEvaluator,
)
from src.evaluations.core.eval.runner.response_manager import ResponseManager
from src.evaluations.core.eval.runner.task_processor import TaskProcessor
from src.evaluations.core.eval.runner.result_analyzer import ResultAnalyzer
from src.evaluations.core.eval.runner.persistence import ResultPersistence
from src.evaluations.core.eval.log import logger
from src.evaluations.core.eval.schemas import ConversationTurn, ReasoningStep
import time
from src.services.eai_gateway.api import EAIClient


class PrecomputedResponseModel(BaseModel):
    """
    Define o schema esperado para cada entrada no arquivo de respostas pré-computadas,
    usado para validação.
    """

    id: str
    one_turn_agent_message: Optional[str] = None
    one_turn_reasoning_trace: Optional[List[ReasoningStep]] = None
    multi_turn_transcript: Optional[List[ConversationTurn]] = None


class AsyncExperimentRunner:
    """
    Orquestra a execução de experimentos de avaliação de agentes de IA,
    delegando responsabilidades para componentes especializados.
    """

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        # agent_config: Dict[str, Any],
        evaluators: List[BaseEvaluator],
        precomputed_responses: Optional[Dict[str, Dict[str, Any]]] = None,
        max_concurrency: int = 10,
        upload_to_bq: bool = True,
        output_dir: Union[str, Path] = "./data",
        provider: str = "google_agent_engine",
        timeout: int = 180,
        polling_interval: int = 2,
        rate_limit_requests_per_minute: int = 60,
    ):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        # self.agent_config = agent_config
        self.evaluators = evaluators
        self.precomputed_responses = precomputed_responses or {}
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.upload_to_bq = upload_to_bq
        self.output_dir = Path(output_dir)
        self.eai_client = EAIClient(
            provider=provider,
            timeout=timeout,
            polling_interval=polling_interval,
            rate_limit_requests_per_minute=rate_limit_requests_per_minute,
        )

        self._evaluator_cache = self._categorize_evaluators()
        self._validate_evaluators()

        if self.precomputed_responses:
            self._validate_precomputed_responses()
            logger.info(
                f"✅ Runner inicializado com {len(self.precomputed_responses)} "
                f"respostas pré-computadas."
            )

    def _validate_precomputed_responses(self) -> None:
        """
        Valida a estrutura e o conteúdo do dicionário de respostas pré-computadas.
        Levanta um erro claro se a validação falhar.
        """
        logger.debug("Validando respostas pré-computadas...")
        for task_id, response_data in self.precomputed_responses.items():
            if not isinstance(response_data, dict):
                raise TypeError(
                    f"Resposta pré-computada para o ID '{task_id}' deve ser um dicionário, "
                    f"mas foi encontrado um {type(response_data).__name__}."
                )

            if response_data.get("id") != task_id:
                raise ValueError(
                    f"Inconsistência de ID na resposta pré-computada. A chave é '{task_id}', "
                    f"mas o campo 'id' interno é '{response_data.get('id')}'."
                )
            try:
                PrecomputedResponseModel.model_validate(response_data)
            except ValidationError as e:
                raise ValueError(
                    f"Erro de validação na resposta pré-computada para o ID '{task_id}':\n{e}"
                ) from e
        logger.debug("Validação das respostas pré-computadas concluída com sucesso.")

    def _categorize_evaluators(self) -> Dict[str, List[BaseEvaluator]]:
        """Categoriza avaliadores por tipo para otimizar acesso."""
        categories: Dict[str, List[BaseEvaluator]] = {
            "one_turn": [],
            "multi_turn": [],
            "conversation": [],
        }
        for evaluator in self.evaluators:
            if isinstance(evaluator, BaseConversationEvaluator):
                categories["conversation"].append(evaluator)
            elif isinstance(evaluator, BaseOneTurnEvaluator):
                categories["one_turn"].append(evaluator)
            elif isinstance(evaluator, BaseMultipleTurnEvaluator):
                categories["multi_turn"].append(evaluator)
            else:
                raise ValueError(
                    f"Tipo de avaliador não suportado: {type(evaluator).__name__}"
                )
        return categories

    def _validate_evaluators(self) -> None:
        """Valida a configuração dos avaliadores."""
        if len(self._evaluator_cache["conversation"]) > 1:
            raise ValueError(
                "Apenas um avaliador do tipo 'conversation' é permitido por experimento."
            )
        if (
            self._evaluator_cache["multi_turn"]
            and not self._evaluator_cache["conversation"]
        ):
            raise ValueError(
                "Avaliadores 'multi' requerem um avaliador 'conversation'."
            )

    def _generate_experiment_id(self) -> int:
        """Gera ID único para o experimento."""
        exp_hash = hashlib.sha256(
            f"{self.experiment_name}_{datetime.now(timezone.utc).isoformat()}_{uuid.uuid4().hex}".encode()
        ).hexdigest()
        return int(exp_hash[:16], 16) & (2**63 - 1)

    async def run(self, loader: DataLoader) -> Dict[str, Any]:
        """
        Executa o experimento completo.
        """
        logger.info(f"Iniciando experimento: {self.experiment_name}")
        start_time = time.perf_counter()

        tasks = list(loader.get_tasks())
        if not tasks:
            raise ValueError("Nenhuma tarefa encontrada no loader.")
        logger.info(f"Carregadas {len(tasks)} tarefas para processamento.")

        # Inicializa os componentes
        response_manager = ResponseManager(
            precomputed_responses=self.precomputed_responses,
            eai_client=self.eai_client,
            timeout=self.eai_client.timeout,
            polling_interval=self.eai_client.polling_interval,
            rate_limit_requests_per_minute=self.eai_client.rate_limiter.requests_per_minute,
        )
        task_processor = TaskProcessor(self._evaluator_cache, response_manager)
        result_analyzer = ResultAnalyzer()
        persistence = ResultPersistence(
            self.output_dir, self.experiment_name, self.upload_to_bq
        )

        # Executa as tarefas em paralelo
        async def process_with_semaphore(task):
            async with self.semaphore:
                return await task_processor.process(task)

        runs = await tqdm_asyncio.gather(
            *[process_with_semaphore(task) for task in tasks],
            desc=f"Executando: {self.experiment_name}",
        )

        total_duration = time.perf_counter() - start_time

        # Analisa e monta o resultado final
        logger.info("Calculando métricas agregadas...")
        analysis_summary = result_analyzer.analyze(runs, total_duration)
        dataset_config = loader.get_dataset_config()

        final_result = {
            "dataset_name": dataset_config.get("dataset_name"),
            "dataset_description": dataset_config.get("dataset_description"),
            "dataset_id": dataset_config.get("dataset_id"),
            "experiment_id": self._generate_experiment_id(),
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "experiment_timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_metadata": self.metadata,
            **analysis_summary,
            "runs": runs,
        }

        # Salva os resultados
        await persistence.save(final_result)

        logger.info(
            f"Experimento '{self.experiment_name}' concluído em "
            f"{analysis_summary['execution_summary']['total_duration_seconds']}s"
        )

        await self.eai_client.close()
        logger.info("EAI Client encerrado.")
        return final_result
