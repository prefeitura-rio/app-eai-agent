from fastapi import APIRouter
from src.api.v1.eai_gateway import router as eai_gateway_router
from src.api.v1.auth import router as auth_router
from src.api.v1.experiments import router as experiments_router
from src.api.v1.experiments_phoenix import router as experiments_phoenix_router
from src.api.v1.webhook import router as webhook_router
from src.api.v1.agent_config import router as agent_config_router
from src.api.v1.system_prompt import router as system_prompt_router
from src.api.v1.unified_history import router as unified_history_router
from src.api.v1.unified_reset import router as unified_reset_router
from src.api.v1.unified_save import router as unified_save_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(eai_gateway_router)
router.include_router(webhook_router)
router.include_router(agent_config_router)
router.include_router(system_prompt_router)
router.include_router(unified_history_router)
router.include_router(unified_reset_router)
router.include_router(unified_save_router)
router.include_router(experiments_phoenix_router)
router.include_router(experiments_router)
