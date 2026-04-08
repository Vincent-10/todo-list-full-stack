"""
API v1 router - aggregates all v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.tags import router as tags_router
from app.api.v1.tasks import router as tasks_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(tags_router)
api_router.include_router(tasks_router)
