from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from src.services.phoenix.dependencies import (
    PhoenixServiceDep,
    DataProcessorDep,
)
from src.services.phoenix.schemas import ExperimentData
from src.core.security.dependencies import validar_token
from src.utils.log import logger

# Configurações e constantes
router = APIRouter(dependencies=[Depends(validar_token)], tags=["Phoenix Experiments"])


# ==================== ROTAS ====================


@router.get("/datasets_data")
async def get_datasets_data(phoenix_service: PhoenixServiceDep):
    """Dados dos datasets."""
    return await phoenix_service.get_datasets()


@router.get("/dataset_experiments_data")
async def get_dataset_data(dataset_id: str, phoenix_service: PhoenixServiceDep):
    """Dados de um dataset específico."""
    return await phoenix_service.get_dataset_experiments(dataset_id=dataset_id)


@router.get("/dataset_examples_data")
async def get_dataset_examples(
    dataset_id: str,
    phoenix_service: PhoenixServiceDep,
    first: int = 1000,
    after: Optional[str] = None,
):
    """Exemplos de um dataset específico."""
    return await phoenix_service.get_dataset_examples(
        dataset_id=dataset_id, first=first, after=after
    )


@router.get("/experiment_data", response_model=ExperimentData)
async def get_experiment_data(
    dataset_id: str,
    experiment_id: str,
    phoenix_service: PhoenixServiceDep,
    data_processor: DataProcessorDep,
):
    """Dados de um experimento específico."""
    try:
        # Buscar dados do experimento
        raw_data = await phoenix_service.get_experiment_json_data(
            experiment_id=experiment_id
        )

        # Processar dados
        processed_data = data_processor.process_experiment_output(output=raw_data)

        # Enriquecer com informações adicionais
        result = ExperimentData(
            dataset_id=dataset_id,
            experiment_id=experiment_id,
            dataset_name=await phoenix_service.get_dataset_name(dataset_id=dataset_id),
            experiment_name=await phoenix_service.get_experiment_name(
                dataset_id=dataset_id, experiment_id=experiment_id
            ),
            experiment_metadata=processed_data.get("experiment_metadata", {}),
            experiment=processed_data.get("experiment", []),
        )

        return result
    except Exception as e:
        logger.error(
            f"Failed to get experiment data for experiment_id={experiment_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching data for experiment {experiment_id}.",
        )


@router.get("/experiment_data_clean", response_model=ExperimentData)
async def get_experiment_data_clean(
    dataset_id: str,
    experiment_id: str,
    phoenix_service: PhoenixServiceDep,
    data_processor: DataProcessorDep,
    number_of_random_experiments: Optional[int] = 10,
    filters: Optional[str] = None,
):
    """
    Dados de um experimento específico, limpos e organizados.
    Se number_of_random_experiments for fornecido, retorna um número aleatório de experimentos.
    Se filters for fornecido, aplica filtros específicos (JSON string).
    Apenas para download!
    """
    raw_data = await phoenix_service.get_experiment_json_data(
        experiment_id=experiment_id
    )
    processed_data = data_processor.process_experiment_output(output=raw_data)

    # Parse filters if provided
    filter_config = None
    if filters:
        import json

        try:
            filter_config = json.loads(filters)
        except json.JSONDecodeError:
            # Se houver erro no JSON, ignorar filtros
            filter_config = None

    clean_experiment = data_processor.get_experiment_json_data_clean(
        processed_data=processed_data,
        number_of_random_experiments=number_of_random_experiments,
        filter_config=filter_config,
    )

    # Enriquecer com informações adicionais
    result = ExperimentData(
        dataset_id=dataset_id,
        experiment_id=experiment_id,
        dataset_name=await phoenix_service.get_dataset_name(dataset_id=dataset_id),
        experiment_name=await phoenix_service.get_experiment_name(
            dataset_id=dataset_id, experiment_id=experiment_id
        ),
        experiment_metadata=clean_experiment.get("experiment_metadata", {}),
        experiment=clean_experiment.get("experiment", []),
    )

    return result
