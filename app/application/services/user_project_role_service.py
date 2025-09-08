from uuid import UUID

from app.application.services import AuthService
from app.core.exceptions import DatabaseError
from app.domain.enities import Project, User
from app.domain.enities.user_project_role import RoleEnum, UserProjectRole
from app.domain.exceptions.user_project_role_exceptions import (
    ProjectRoleAddByUsernameError, ProjectRoleAddNotAuthorizedError,
    ProjectRoleAlreadyAssignedError, ProjectRoleCreateError,
    ProjectRoleReadError)
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.user_project_role_repository import \
    UserProjectRoleRepository
from app.domain.repositories.user_repository import UserRepository
from app.presentation.schemas.auth_schemas import UserOut


class UserProjectRoleService:
    def __init__(self, repo: UserProjectRoleRepository, user_repo: UserRepository, project_repo=ProjectRepository):
        self.repo = repo
        self.user_repo = user_repo
        self.project_repo = project_repo

    def add_role(self, project_id: UUID, user_id: UUID, role: RoleEnum = RoleEnum.PARTICIPANT):
        role_model = UserProjectRole(project_id=project_id, user_id=user_id, role=role)
        try:
            return self.repo.add(role_model=role_model)
        except DatabaseError as e:
            raise ProjectRoleCreateError(project_id=project_id, role=str(role)) from e

    def add_participant_by_username(self, project_id: UUID, username: str, current_user: UserOut):
        """Invite a participant to a project"""

        role = RoleEnum.PARTICIPANT

        # check if the current user, has the owner rights on the project and is authorized to invite participants
        current_user_role_on_project = self.repo.get_user_role_on_project(
            project_id=project_id, user_id=current_user.id
        )
        if current_user_role_on_project != RoleEnum.OWNER:
            raise ProjectRoleAddNotAuthorizedError(username=current_user.username)

        # check if the invited user exists
        user = self.user_repo.get_by_username(username=username)
        if user is None:
            raise ProjectRoleAddByUsernameError(username=username)

        # check if the invited participant is not already a participant of this project
        project_role = self.repo.get_user_role_on_project(project_id=project_id, user_id=user.id)
        if project_role is not None:
            raise ProjectRoleAlreadyAssignedError(username=user.username)

        # create a new role model
        role_model = UserProjectRole(project_id=project_id, user_id=user.id, role=role)

        # save project role to database
        try:
            self.repo.add(role_model=role_model)
        except DatabaseError as e:
            raise ProjectRoleCreateError(project_id=project_id, role=role) from e

    def get_user_role_on_project(self, project_id: UUID, user_id: UUID):
        """Returns a user role by project"""
        try:
            self.repo.get_user_role_on_project(project_id=project_id, user_id=user_id)
        except DatabaseError as e:
            raise ProjectRoleReadError(user_id=user_id, project_id=project_id) from e
