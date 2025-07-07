"""
Módulo de dependências para injeção de dependências do FastAPI.
Este módulo centraliza a criação e configuração de serviços.
"""

import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from src.admin.experiments.utils import (
    PhoenixConfig,
    PhoenixService,
    ExperimentDataProcessor,
    FrontendManager,
)
from src.config import env
from loguru import logger


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


@lru_cache()
def get_frontend_manager() -> FrontendManager:
    """
    Cria e retorna uma instância do FrontendManager.
    Usa cache pois as configurações são estáticas.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    admin_static_dir = os.path.join(os.path.dirname(base_dir), "static")

    logger.info(f"Diretório estático de experimentos: {static_dir}")

    return FrontendManager(
        static_dir=static_dir,
        admin_static_dir=admin_static_dir,
        use_local_api=env.USE_LOCAL_API,
        base_url_local="http://localhost:8089/eai-agent",
        base_url_staging="https://services.staging.app.dados.rio/eai-agent",
    )


# Tipos anotados para facilitar o uso
PhoenixServiceDep = Annotated[PhoenixService, Depends(get_phoenix_service)]
DataProcessorDep = Annotated[ExperimentDataProcessor, Depends(get_data_processor)]
FrontendManagerDep = Annotated[FrontendManager, Depends(get_frontend_manager)]
