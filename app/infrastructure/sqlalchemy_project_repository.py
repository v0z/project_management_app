import uuid
from typing import cast

from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import DatabaseError
from app.domain.enities import Project
from app.domain.enities.project import Project as DomainProject
from app.domain.enities.document import Document
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.orm import ProjectORM


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain_entity(orm: ProjectORM) -> DomainProject:
        """Map ORM model to domain model"""

        # loop through all documents and wrap them in a Document model
        documents = [
            Document(
                id=doc.id,
                file_name=doc.file_name,
                content_type=doc.content_type,
                project_id=doc.project_id,
                storage_path=doc.storage_path,
                created_at=doc.created_at,
            )
            for doc in orm.documents
        ]

        # add the document list to the project
        return DomainProject(
            id=cast(uuid.UUID, orm.id),
            name=orm.name,
            description=orm.description,
            owner=cast(uuid.UUID, orm.owner_id),
            created_at=orm.created_at,
            documents=documents,
        )

    @staticmethod
    def _to_orm(entity: Project) -> ProjectORM:
        """Map from domain model to ORM model"""
        return ProjectORM(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            owner_id=entity.owner,
            created_at=entity.created_at,
        )

    def list_by_user(self, user_id: UUID) -> list[DomainProject]:
        """List all projects for a given user ID"""
        try:
            orm_projects = (
                self.db.query(ProjectORM)
                .options(joinedload(ProjectORM.documents))
                .filter(ProjectORM.owner_id == user_id)
                .all()
            )
            return [self._to_domain_entity(orm) for orm in orm_projects]
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def get_by_id(self, project_id: UUID) -> DomainProject | None:
        """Get a project by its ID"""
        try:
            orm = self.db.get(entity=ProjectORM, ident=project_id)
            if orm is None:
                # I do not throw NotFound exception here but in service instead
                return None
            return self._to_domain_entity(orm)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def add(self, project: DomainProject) -> DomainProject:
        """Add a new project to the database"""
        orm = ProjectORM(id=project.id, name=project.name, description=project.description, owner_id=project.owner)
        try:
            self.db.add(orm)
            self.db.commit()
            self.db.refresh(orm)
            return self._to_domain_entity(orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e

    def save(self, project: Project) -> Project:
        """Persist changes to an existing project"""
        try:
            orm = self._to_orm(entity=project)
            self.db.merge(orm)
            self.db.commit()
            return project
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e

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
            raise DatabaseError(str(e)) from e
