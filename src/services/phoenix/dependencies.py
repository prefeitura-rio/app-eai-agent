"""
Módulo de dependências para injeção de dependências do FastAPI.
Este módulo centraliza a criação e configuração de serviços.
"""

import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from src.services.phoenix.utils import (
    PhoenixConfig,
    PhoenixService,
    ExperimentDataProcessor,
)
from src.config import env


@lru_cache()
def get_phoenix_config() -> PhoenixConfig:
    """
    Cria e retorna a configuração do Phoenix.
    Usa cache para evitar recriar a configuração a cada chamada.
    """
    return PhoenixConfig(endpoint=env.PHOENIX_ENDPOINT)


def get_phoenix_service(
    config: Annotated[PhoenixConfig, Depends(get_phoenix_config)],
) -> PhoenixService:
    """
    Cria e retorna uma instância do PhoenixService.
    """
    return PhoenixService(config=config)


def get_data_processor() -> ExperimentDataProcessor:
    """
    Cria e retorna uma instância do ExperimentDataProcessor.
    """
    return ExperimentDataProcessor()


# Tipos anotados para facilitar o uso
PhoenixServiceDep = Annotated[PhoenixService, Depends(get_phoenix_service)]
DataProcessorDep = Annotated[ExperimentDataProcessor, Depends(get_data_processor)]
