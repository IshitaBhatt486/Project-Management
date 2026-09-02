from fastapi import APIRouter

from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.health import router as health_router
from backend.api.routes.projects import router as projects_router
from backend.api.routes.tasks import router as tasks_router

router = APIRouter()
router.include_router(health_router)
router.include_router(projects_router)
router.include_router(tasks_router)
router.include_router(dashboard_router)