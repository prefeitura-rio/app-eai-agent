from fastapi import APIRouter
from src.api.v1.test_letta import router as letta_router

router = APIRouter(prefix="/v1")
router.include_router(letta_router)
