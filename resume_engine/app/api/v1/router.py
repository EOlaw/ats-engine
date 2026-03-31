"""API v1 router — includes all endpoint sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.export import router as export_router
from app.api.v1.endpoints.resume import router as resume_router
from app.api.v1.endpoints.upload import router as upload_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(resume_router)
api_router.include_router(analysis_router)
api_router.include_router(export_router)
