from fastapi import APIRouter
from src.admin.routes import router as admin_router

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(admin_router) 