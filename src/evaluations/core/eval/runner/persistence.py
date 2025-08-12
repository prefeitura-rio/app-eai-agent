# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Dict, Any

from src.utils.bigquery import upload_experiment_to_bq
from src.evaluations.core.eval.log import logger


class ResultPersistence:
    """
    Gerencia a persistência dos resultados do experimento,
    seja em arquivos locais ou em serviços como o BigQuery.
    """

    def __init__(self, output_dir: Path, experiment_name: str, upload_to_bq: bool):
        self.output_dir = output_dir
        self.experiment_name = experiment_name
        self.upload_to_bq = upload_to_bq

    async def save(self, final_result: Dict[str, Any]) -> None:
        """
        Salva o resultado final do experimento.

        Args:
            final_result: O dicionário completo com os resultados.
        """
        output_path = await self._save_to_json(final_result)

        if self.upload_to_bq:
            try:
                logger.info("Fazendo upload para BigQuery...")
                upload_experiment_to_bq(result_data=final_result)
                logger.info("Upload para BigQuery concluído")
            except Exception as e:
                logger.error(f"Erro no upload para BigQuery: {e}")
                # Não falha o experimento por erro de upload

        logger.info(f"Resultados salvos em: {output_path}")

    async def _save_to_json(self, final_result: Dict[str, Any]) -> Path:
        """Salva resultados em arquivo JSON."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"results_{self.experiment_name}.json"

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)
            return output_path
        except Exception as e:
            logger.error(f"Erro ao salvar resultados em JSON: {e}")
            raise
