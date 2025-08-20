import uuid
from typing import List, Optional, cast

from sqlalchemy import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.enities import Project
from app.domain.enities.project import Project as DomainProject
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.orm.project_model import ProjectORM
from app.presentation.schemas.project_schemas import ProjectUpdateRequest
from app.core.exceptions import DatabaseError


class SQLAlchemyProjectRepository(ProjectRepository):
	def __init__(self, db: Session):
		self.db = db

	@staticmethod
	def _to_domain_entity(orm: ProjectORM) -> DomainProject:
		"""Map ORM model to domain model"""
		return DomainProject(
			id=cast(uuid.UUID, orm.id),
			name=orm.name,
			description=orm.description,
			owner=cast(uuid.UUID, orm.owner_id),
			created_at=orm.created_at,
		)

	def list_by_user(self, user_id: UUID) -> List[DomainProject]:
		"""List all projects for a given user ID"""
		try:
			orm_projects = self.db.query(ProjectORM).filter(ProjectORM.owner_id == user_id).all()
			return [self._to_domain_entity(orm) for orm in orm_projects]
		except SQLAlchemyError as e:
			raise DatabaseError("Failed to fetch projects") from e
		except Exception:
			raise

	def add(self, project: DomainProject) -> DomainProject:
		"""Add a new project to the database"""
		orm = ProjectORM(
			id=project.id,
			name=project.name,
			description=project.description,
			owner_id=project.owner,
		)
		try:
			self.db.add(orm)
			self.db.commit()
			self.db.refresh(orm)
			return self._to_domain_entity(orm)
		except SQLAlchemyError as e:
			self.db.rollback()
			raise DatabaseError("Failed to save project") from e
		except Exception:
			raise

	def get_by_id(self, project_id: UUID) -> Optional[DomainProject]:
		"""Get a project by its ID"""
		try:
			orm = self.db.get(entity=ProjectORM, ident=project_id)
			if orm is None:
				# I do not throw NotFound exception here but in service instead
				return None
			return self._to_domain_entity(orm)
		except SQLAlchemyError as e:
			raise DatabaseError("Failed to get project") from e

	def update(self, project_id: UUID, data: ProjectUpdateRequest) -> Optional[Project]:
		"""Update a project"""

		orm = self.db.get(entity=ProjectORM, ident=project_id)
		if orm is None:
			return None

		# Skip fields that are not in the update model
		for field, value in data.model_dump(exclude_unset=True).items():
			setattr(orm, field, value)

		try:
			self.db.commit()
			self.db.refresh(orm)
			return self._to_domain_entity(orm)
		except SQLAlchemyError:
			self.db.rollback()
			raise DatabaseError("Failed to update project")

	def delete(self, project_id: UUID) -> bool:
		"""Delete a project by ID. Returns True if deleted, False if not found."""
		try:
			orm = self.db.get(entity=ProjectORM, ident=project_id)
			if orm is None:
				return False

			self.db.delete(orm)
			self.db.commit()
			return True

		except SQLAlchemyError as e:
			self.db.rollback()
			raise DatabaseError("Failed to delete project") from e
