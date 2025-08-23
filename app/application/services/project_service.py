from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.exceptions import DatabaseError
from app.domain.enities import Project
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.domain.exceptions.project_exceptions import (
    ProjectCreateError,
    ProjectDeleteError,
    ProjectNotFoundError,
    ProjectPermissionError,
    ProjectRetrieveError,
    ProjectUpdateError,
)
from app.domain.repositories.project_repository import ProjectRepository
from app.presentation.schemas.project_schemas import ProjectUpdateRequest


class ProjectService:
  
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    def add_project(self, name: str, description: str, user_id: UUID) -> Project:
        # name uniqueness is not enforced, so I don't check it
        try:
            project = Project(
                id=uuid4(), name=name, description=description, owner=user_id, created_at=datetime.now(timezone.utc)
            )
            return self.repo.add(project=project)
        except DomainValidationError as e:
            raise ProjectCreateError(str(e)) from e
        except DatabaseError as e:
            raise ProjectCreateError(str(e)) from e

    def get_all_projects(self, user_id: UUID) -> list[Project]:
        try:
            # return a list of all projects
            return self.repo.list_by_user(user_id=user_id)
        except DatabaseError as e:
            raise ProjectRetrieveError(str(e)) from e

    def get_project(self, project_id: UUID, user_id: UUID) -> Project:
        project = self.repo.get_by_id(project_id=project_id)
        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check the ownership (only owners can view)
        if not project.is_owned_by(user_id=user_id):
            raise ProjectPermissionError()

        return project

    def update_project(self, project_id: UUID, user_id: UUID, data: ProjectUpdateRequest) -> Project:
        project = self.repo.get_by_id(project_id=project_id)
        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check ownership
        if not project.is_owned_by(user_id=user_id):
            raise ProjectPermissionError()

        # only include fields that were actually sent
        update_data = data.model_dump(exclude_unset=True)

        # pass them as keyword arguments to update()
        project.update(**update_data)

        try:
            # save the changes
            return self.repo.save(project)
        except DatabaseError as e:
            raise ProjectUpdateError(str(e)) from e

    def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        project = self.repo.get_by_id(project_id=project_id)

        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check project ownership here, not in the repository
        if not project.is_owned_by(user_id=user_id):
            raise ProjectPermissionError()

        deleted = self.repo.delete(project_id=project_id)
        if not deleted:
            raise ProjectDeleteError()
        return deleted