from fastapi import APIRouter
from src.api.v1.test_letta import router as letta_router
from src.api.v1.webhook import router as webhook_router
from src.api.v1.tools import router as tools_router
from src.api.v1.system_prompt import router as system_prompt_router
from src.api.v1.external_tools import router as external_tools_router

router = APIRouter(prefix="/v1")

router.include_router(letta_router)
router.include_router(webhook_router)
router.include_router(tools_router)
router.include_router(system_prompt_router)
router.include_router(external_tools_router)
