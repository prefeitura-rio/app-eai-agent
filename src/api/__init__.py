from fastapi import APIRouter
from src.api.v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)