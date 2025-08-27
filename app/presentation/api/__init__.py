from app.presentation.api.v1.auth_routes import router as auth_router
from app.presentation.api.v1.document_routes import router as document_router
from app.presentation.api.v1.project_routes import router as project_router

__all__ = ["auth_router", "project_router", "document_router"]
