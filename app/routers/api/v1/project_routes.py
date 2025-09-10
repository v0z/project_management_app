from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domain.exceptions.project_exceptions import (ProjectCreateError,
                                                      ProjectDeleteError,
                                                      ProjectNotFoundError,
                                                      ProjectPermissionError,
                                                      ProjectRetrieveError,
                                                      ProjectUpdateError)
from app.domain.exceptions.user_project_role_exceptions import (
    ProjectRoleAddByUsernameError, ProjectRoleAddNotAuthorizedError,
    ProjectRoleCreateError)
from app.infrastructure.core.exceptions import DatabaseError
from app.infrastructure.core.logger import logger
from app.routers.dependencies import (get_current_user, get_project_service,
                                      get_role_service_provider)
from app.routers.schemas.auth_schemas import UserOut
from app.routers.schemas.project_schemas import (ProjectCreateRequest,
                                                 ProjectFullDetails,
                                                 ProjectResponse,
                                                 ProjectUpdateRequest)
from app.services import ProjectService, UserProjectRoleService

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{project_id}", response_model=ProjectFullDetails, summary="Get a project", status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except ProjectUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete("/{project_id}", summary="Delete project", status_code=status.HTTP_200_OK)
async def delete(
    project_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    """Delete a project by id"""
    try:
        await service.delete_project(project_id=project_id, user_id=current_user.id)
        # instead of 204 "No content", returning an informative response
        return {"message": f"Project with ID: {project_id} was successfully deleted"}
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except ProjectDeleteError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post("/{project_id}/invite")
async def invite_user(
    project_id: UUID,
    username: str | None = Query(None),
    current_user: UserOut = Depends(get_current_user),
    role_service: UserProjectRoleService = Depends(get_role_service_provider),
):
    """Grant access to the project for a specific user."""
    try:
        role_service.add_participant_by_username(project_id=project_id, username=username, current_user=current_user)
        return {"message": f"user '{username}' has been invited to project {project_id}"}
    except ProjectRoleAddNotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except ProjectRoleAddByUsernameError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (ProjectRoleCreateError, Exception) as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
