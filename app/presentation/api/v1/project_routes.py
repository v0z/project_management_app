from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.project_service import ProjectService
from app.core.exceptions import DatabaseError
from app.core.logger import logger
from app.domain.exceptions.project_exceptions import (
    ProjectCreateError,
    ProjectDeleteError,
    ProjectNotFoundError,
    ProjectPermissionError,
    ProjectRetrieveError,
    ProjectUpdateError,
)
from app.presentation.dependencies import get_current_user, get_project_service
from app.presentation.schemas.auth_schemas import UserOut
from app.presentation.schemas.project_schemas import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse], summary="Show all projects", status_code=status.HTTP_200_OK)
async def list_all(
    service: ProjectService = Depends(get_project_service), current_user: UserOut = Depends(get_current_user)
):
    """Show all projects that belong to the authenticated user"""
    try:
        return service.get_all_projects(user_id=current_user.id)
    except ProjectRetrieveError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from e


@router.post("/", response_model=ProjectResponse, summary="Create project", status_code=status.HTTP_201_CREATED)
async def create(
    form: ProjectCreateRequest,
    current_user: UserOut = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):

    """Create a project and add it to the user"""
    try:
        # return the created project
        return service.add_project(name=form.name, description=form.description, user_id=current_user.id)
    except ProjectCreateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get a project", status_code=status.HTTP_200_OK)
async def get_project(
    project_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    """Get a project by id"""
    try:
        # return the retrieved project
        return service.get_project(project_id=project_id, user_id=current_user.id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e


@router.patch("/{project_id}", summary="Update project", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def update(
    project_id: UUID,
    project_data: ProjectUpdateRequest,
    current_user: UserOut = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    """Update a project by id"""
    try:
        # return the updated project
        return service.update_project(project_id=project_id, user_id=current_user.id, data=project_data)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e
    except ProjectUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e


@router.delete("/{project_id}", summary="Delete project", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    project_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    """Delete a project by id"""
    try:
        service.delete_project(project_id=project_id, user_id=current_user.id)
        # status 204 "No content" is returned so there’s no response body
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e
    except ProjectDeleteError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e
