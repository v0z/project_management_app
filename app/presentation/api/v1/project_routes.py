from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.project_service import ProjectService
from app.domain.enities import User
from app.presentation.dependencies import get_current_user, get_project_service, get_user_repository
from app.presentation.schemas.auth_schemas import UserOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", summary="Create project", status_code=status.HTTP_201_CREATED)
async def create(name: str, description: str, current_user: UserOut = Depends(get_current_user),
                 project_service: ProjectService = Depends(get_project_service)):
    """ Create a project and add it to the user"""
    try:
        project = project_service.add_project(
            name=name,
            description=description,
            user_id=current_user.id
        )
        return project
    except Exception as e:
        # raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        raise
