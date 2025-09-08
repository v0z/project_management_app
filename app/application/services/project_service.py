from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.application.services.user_project_role_service import \
    UserProjectRoleService
from app.core.exceptions import DatabaseError
from app.domain.enities import Project
from app.domain.enities.user_project_role import RoleEnum
from app.domain.exceptions.document_exceptions import DocumentFileDeleteError
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.domain.exceptions.project_exceptions import (ProjectCreateError,
                                                      ProjectDeleteError,
                                                      ProjectNotFoundError,
                                                      ProjectPermissionError,
                                                      ProjectRetrieveError,
                                                      ProjectUpdateError)
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.storage.document_storage import DocumentStorage
from app.presentation.schemas.project_schemas import ProjectUpdateRequest


class ProjectService:
    def __init__(self, repo: ProjectRepository, storage: DocumentStorage, role_service: UserProjectRoleService):
        self.repo = repo
        self.storage = storage
        self.role_service = role_service

    def add_project(self, name: str, description: str, user_id: UUID) -> Project:
        # name uniqueness is not enforced, so I don't check it
        try:
            project = Project(
                id=uuid4(), name=name, description=description, owner=user_id, created_at=datetime.now(UTC)
            )

            # save the project to db
            project = self.repo.add(project=project)

            # add a role to the associated table after project is saved
            self.role_service.add_role(project_id=project.id, user_id=user_id, role=RoleEnum.OWNER)
            return project
        except DomainValidationError as e:
            raise ProjectCreateError(str(e)) from e
        except DatabaseError as e:
            raise ProjectCreateError(str(e)) from e

    def get_all_projects(self, user_id: UUID) -> list[Project]:
        """Returns all projects in which the user participates"""
        try:
            return self.repo.list_by_user(user_id=user_id)
        except DatabaseError as e:
            raise ProjectRetrieveError(str(e)) from e

    def get_project(self, project_id: UUID, user_id: UUID) -> Project:
        project = self.repo.get_by_id(project_id=project_id)
        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check if user is a participant in this project
        if not self.is_project_participant(project=project, user_id=user_id):
            raise ProjectPermissionError

        # all good - return project
        return project

    def update_project(self, project_id: UUID, user_id: UUID, data: ProjectUpdateRequest) -> Project:
        project = self.repo.get_by_id(project_id=project_id)
        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check if user is a participant in this project
        if not self.is_project_participant(project=project, user_id=user_id):
            raise ProjectPermissionError

        # only include fields that were actually sent
        update_data = data.model_dump(exclude_unset=True)

        # pass them as keyword arguments to update()
        project.update(**update_data)

        try:
            # save the changes
            return self.repo.save(project)
        except DatabaseError as e:
            raise ProjectUpdateError(str(e)) from e

    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        project = self.repo.get_by_id(project_id=project_id)

        if project is None:
            raise ProjectNotFoundError(project_id=project_id)

        # check project ownership here, not in the repository
        # if not project.is_owned_by(user_id=user_id):
        #     raise ProjectPermissionError()

        # check if user has owner rights
        if not self.is_project_owner(project=project, user_id=user_id):
            raise ProjectPermissionError

        try:
            # get all the paths to the documents
            storage_paths = [doc.storage_path for doc in project.documents]

            # delete the files from storage
            for path in storage_paths:
                # doc_service.delete_file(storage_path=path)
                await self.storage.remove(storage_path=path)

            # delete the project from the database
            deleted = self.repo.delete(project_id=project_id)

            if not deleted:
                raise ProjectDeleteError("Repository deletion returned false")

            return deleted
        except (DatabaseError, DocumentFileDeleteError) as e:
            raise ProjectDeleteError(str(e)) from e

    @staticmethod
    def is_project_owner(project: Project, user_id: UUID) -> bool:
        """Check if given user has owner role on the project"""
        return any([p.user_id == user_id and p.role == RoleEnum.OWNER for p in project.participants])

    @staticmethod
    def is_project_participant(project: Project, user_id: UUID) -> bool:
        """Check if user is a participant on the project"""
        return any([p.user_id == user_id and p.role is not None for p in project.participants])
