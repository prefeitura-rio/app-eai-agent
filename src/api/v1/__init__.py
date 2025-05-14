from fastapi import APIRouter
from src.api.v1.test_letta import router as letta_router
from src.api.v1.webhook import router as webhook_router

router = APIRouter(prefix="/v1")
router.include_router(letta_router)
router.include_router(webhook_router)
