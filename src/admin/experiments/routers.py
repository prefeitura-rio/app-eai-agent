import os
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from src.admin.experiments.utils import (
    PhoenixConfig,
    PhoenixService,
    ExperimentDataProcessor,
    FrontendManager,
)
from src.config import env
from loguru import logger

# Configurações e constantes
router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
ADMIN_STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")

logger.info(f"Diretório estático de experimentos: {STATIC_DIR}")

# Inicialização dos serviços
phoenix_service = PhoenixService(config=PhoenixConfig(endpoint=env.PHOENIX_ENDPOINT))
data_processor = ExperimentDataProcessor()
frontend_manager = FrontendManager(
    static_dir=STATIC_DIR,
    admin_static_dir=ADMIN_STATIC_DIR,
    use_local_api=env.USE_LOCAL_API,
    base_url_local="http://localhost:8089/eai-agent",
    base_url_staging="https://services.staging.app.dados.rio/eai-agent",
)


# ==================== ROTAS ====================


@router.get("/favicon.ico")
async def get_favicon():
    """Serve o favicon do admin."""
    return frontend_manager.serve_favicon()


@router.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """Serve arquivos estáticos."""
    return frontend_manager.serve_static_file(file_path=file_path)


@router.get("/auth", response_class=HTMLResponse)
async def get_auth_page():
    """Página de autenticação."""
    return frontend_manager.render_html_page(template_name="auth.html")


@router.get("/data")
async def get_datasets_data():
    """Dados dos datasets."""
    return JSONResponse(content=await phoenix_service.get_datasets())


@router.get("/", response_class=HTMLResponse)
async def get_datasets_page():
    """Página principal de visualização de datasets."""
    return frontend_manager.render_html_page(template_name="datasets.html")


@router.get("/{dataset_id}/data")
async def get_dataset_data(dataset_id: str):
    """Dados de um dataset específico."""
    return JSONResponse(
        content=await phoenix_service.get_dataset_experiments(dataset_id=dataset_id)
    )


@router.get("/{dataset_id}/examples")
async def get_dataset_examples(
    dataset_id: str, first: int = 1000, after: Optional[str] = None
):
    """Exemplos de um dataset específico."""
    return JSONResponse(
        content=await phoenix_service.get_dataset_examples(
            dataset_id=dataset_id, first=first, after=after
        )
    )


@router.get("/{dataset_id}/{experiment_id}/data")
async def get_experiment_data(dataset_id: str, experiment_id: str):
    """Dados de um experimento específico."""
    # Buscar dados do experimento
    raw_data = await phoenix_service.get_experiment_json_data(
        experiment_id=experiment_id
    )

    # Processar dados
    processed_data = data_processor.process_experiment_output(output=raw_data)

    # Enriquecer com informações adicionais
    processed_data.update(
        {
            "dataset_id": dataset_id,
            "experiment_id": experiment_id,
            "dataset_name": await phoenix_service.get_dataset_name(
                dataset_id=dataset_id
            ),
            "experiment_name": await phoenix_service.get_experiment_name(
                dataset_id=dataset_id, experiment_id=experiment_id
            ),
        }
    )

    return JSONResponse(content=processed_data)


@router.get("/{dataset_id}/{experiment_id}", response_class=HTMLResponse)
async def get_experiment_page(dataset_id: str, experiment_id: str):
    """Página de visualização de um experimento específico."""
    return frontend_manager.render_html_page(
        template_name="experiment.html",
        replacements={"DATASET_ID": dataset_id, "EXPERIMENT_ID": experiment_id},
    )


@router.get("/{dataset_id}", response_class=HTMLResponse)
async def get_dataset_experiments_page(dataset_id: str):
    """Página de experimentos de um dataset específico."""
    return frontend_manager.render_html_page(
        template_name="dataset-experiments.html",
        replacements={"DATASET_ID": dataset_id},
    )
