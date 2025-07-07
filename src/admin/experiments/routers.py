from typing import Optional

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.admin.experiments.dependencies import (
    PhoenixServiceDep,
    DataProcessorDep,
    FrontendManagerDep,
)
from src.admin.experiments.schemas import (
    ExperimentData,
    ExperimentRunClean,
)

# Configurações e constantes
router = APIRouter()


# ==================== ROTAS ====================


@router.get("/favicon.ico")
async def get_favicon(frontend_manager: FrontendManagerDep):
    """Serve o favicon do admin."""
    return frontend_manager.serve_favicon()


@router.get("/static/{file_path:path}")
async def get_static_file(file_path: str, frontend_manager: FrontendManagerDep):
    """Serve arquivos estáticos."""
    return frontend_manager.serve_static_file(file_path=file_path)


@router.get("/auth", response_class=HTMLResponse)
async def get_auth_page(frontend_manager: FrontendManagerDep):
    """Página de autenticação."""
    return frontend_manager.render_html_page(template_name="auth.html")


@router.get("/data")
async def get_datasets_data(phoenix_service: PhoenixServiceDep):
    """Dados dos datasets."""
    return await phoenix_service.get_datasets()


@router.get("/", response_class=HTMLResponse)
async def get_datasets_page(frontend_manager: FrontendManagerDep):
    """Página principal de visualização de datasets."""
    return frontend_manager.render_html_page(template_name="datasets.html")


@router.get("/{dataset_id}/data")
async def get_dataset_data(dataset_id: str, phoenix_service: PhoenixServiceDep):
    """Dados de um dataset específico."""
    return await phoenix_service.get_dataset_experiments(dataset_id=dataset_id)


@router.get("/{dataset_id}/examples")
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


@router.get("/{dataset_id}/{experiment_id}/data", response_model=ExperimentData)
async def get_experiment_data(
    dataset_id: str,
    experiment_id: str,
    phoenix_service: PhoenixServiceDep,
    data_processor: DataProcessorDep,
):
    """Dados de um experimento específico."""
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


@router.get(
    "/{dataset_id}/{experiment_id}/data_clean", response_model=ExperimentRunClean
)
async def get_experiment_data_clean(
    dataset_id: str,
    experiment_id: str,
    phoenix_service: PhoenixServiceDep,
    data_processor: DataProcessorDep,
    number_of_random_experiments: Optional[int] = None,
):
    """
    Dados de um experimento específico, limpos e organizados.
    Se number_of_random_experiments for fornecido, retorna um número aleatório de experimentos.
    Apenas para download!
    """
    raw_data = await phoenix_service.get_experiment_json_data(
        experiment_id=experiment_id
    )
    processed_data = data_processor.process_experiment_output(output=raw_data)
    clean_experiment = data_processor.get_experiment_json_data_clean(
        processed_data=processed_data,
        number_of_random_experiments=number_of_random_experiments,
    )

    # Enriquecer com informações adicionais
    result = ExperimentRunClean(
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


@router.get("/{dataset_id}/{experiment_id}", response_class=HTMLResponse)
async def get_experiment_page(
    dataset_id: str, experiment_id: str, frontend_manager: FrontendManagerDep
):
    """Página de visualização de um experimento específico."""
    return frontend_manager.render_html_page(
        template_name="experiment.html",
        replacements={"DATASET_ID": dataset_id, "EXPERIMENT_ID": experiment_id},
    )


@router.get("/{dataset_id}", response_class=HTMLResponse)
async def get_dataset_experiments_page(
    dataset_id: str, frontend_manager: FrontendManagerDep
):
    """Página de experimentos de um dataset específico."""
    return frontend_manager.render_html_page(
        template_name="dataset-experiments.html",
        replacements={"DATASET_ID": dataset_id},
    )
