"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import tasks, context_entries, categories

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(context_entries.router, prefix="/context", tags=["context"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])