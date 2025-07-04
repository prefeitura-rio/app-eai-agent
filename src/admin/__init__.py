from fastapi import APIRouter
from src.admin.routes import router as admin_router
from src.admin.experiments.routers import router as experiments_router
from src.config import env

if env.USE_LOCAL_API:
    prefix = "/eai-agent/admin"
else:
    prefix = "/admin"

router = APIRouter(prefix=prefix, tags=["Admin"])
router.include_router(admin_router)
router.include_router(experiments_router, prefix="/experiments")
