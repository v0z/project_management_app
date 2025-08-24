import uvicorn
from fastapi import Depends, FastAPI

from app.application.services import AuthService, ProjectService
from app.application.services.document_service import DocumentService
from app.core.database import get_db
from app.core.logger import logger
from app.infrastructure import SQLAlchemyProjectRepository, SQLAlchemyUserRepository
from app.infrastructure.sqlalchemy_documet_repository import SQLAlchemyDocumentRepository
from app.presentation.api import auth_router, project_router, document_router

from app.presentation.dependencies import (
    get_auth_service,
    get_project_repository,
    get_project_service,
    get_user_repository,
    get_document_repository,
    get_document_service,
)

app = FastAPI(title="FastAPI Project Management Mess", version="1.0.0")

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(document_router)


# app.include_router(document_router)


# Dependency injection wiring:
def user_repository_provider(db=Depends(get_db)):
    """Dependency provider for UserRepository"""
    return SQLAlchemyUserRepository(db)


def project_repository_provider(db=Depends(get_db)):
    """Dependency provider for ProjectRepository"""
    return SQLAlchemyProjectRepository(db)


def document_repository_provider(db=Depends(get_db)):
    """Dependency provider for DocumentRepository"""
    return SQLAlchemyDocumentRepository(db)


def auth_service_provider(user_repo=Depends(user_repository_provider)):
    """Dependency provider for AuthService"""
    return AuthService(user_repo)


def project_service_provider(project_repo=Depends(project_repository_provider)):
    """Dependency provider for ProjectService"""
    return ProjectService(project_repo)


def document_service_provider(document_repo=Depends(document_repository_provider)):
    """Dependency provider for DocumentService"""
    return DocumentService(document_repo)


# auth dependencies
app.dependency_overrides[get_user_repository] = user_repository_provider  # type: ignore
app.dependency_overrides[get_auth_service] = auth_service_provider  # type: ignore
# project dependencies
app.dependency_overrides[get_project_repository] = project_repository_provider  # type: ignore
app.dependency_overrides[get_project_service] = project_service_provider  # type: ignore
# document dependencies
app.dependency_overrides[get_document_repository] = document_repository_provider  # type: ignore
app.dependency_overrides[get_document_service] = document_service_provider  # type: ignore


@app.get("/", summary="Health Check", tags=["Health"], response_model=dict)
async def root() -> dict[str, str]:
    """Root endpoint to check if the server is running."""
    logger.info("Health check endpoint hit")
    return {"status": "healthy", "message": "server is up"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)
