from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.exceptions import DatabaseError
from app.domain.enities import Project
from app.domain.exceptions.project_exceptions import (
	ProjectNotFoundError,
	ProjectPermissionError,
	ProjectUpdateFailed,
)
from app.domain.repositories.project_repository import ProjectRepository
from app.presentation.schemas.project_schemas import ProjectUpdateRequest


class ProjectService:
	def __init__(self, repo: ProjectRepository):
		self.repo = repo

	def add_project(self, user_id: UUID, name: str, description: str = "") -> Project:
		# name uniqueness is not enforced, so I don't check it

		project = Project(
			id=uuid4(),
			name=name,
			description=description,
			owner=user_id,
			created_at=datetime.now(timezone.utc),
		)
		try:
			return self.repo.add(project=project)
		except DatabaseError:
			raise

	def get_all_projects(self, user_id: UUID):
		try:
			# return a list of all projects
			return self.repo.list_by_user(user_id=user_id)
		except DatabaseError:
			raise

	def get_project(self, project_id: UUID, user_id: UUID):
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

		# update and persist the changes
		project_updated = self.repo.update(project_id=project_id, data=data)
		if project_updated is None:
			raise ProjectUpdateFailed()
		return project_updated

	def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
		project = self.repo.get_by_id(project_id=project_id)

		if project is None:
			raise ProjectNotFoundError(project_id=project_id)

		# check project ownership here, not in the repository
		if not project.is_owned_by(user_id=user_id):
			raise ProjectPermissionError()

		deleted = self.repo.delete(project_id=project_id)
		if not deleted:
			raise Exception("Was unable to delete project")
		return deleted
