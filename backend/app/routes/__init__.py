"""
EduSynapse Routes Module
"""

from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.assessments import router as assessments_router
from app.routes.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "sessions_router",
    "assessments_router",
    "dashboard_router",
]
