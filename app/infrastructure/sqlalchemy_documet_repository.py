from datetime import datetime, UTC, timezone
from typing import Type, List
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import DatabaseError
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.enities.document import Document

from app.infrastructure.orm import DocumentORM, ProjectORM


class SQLAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain_entity(orm: DocumentORM | List[DocumentORM]) -> list[Document] | Document:
        """Map ORM model to domain model"""
        if isinstance(orm, list):
            # add the document list to the project
            return [
                Document(
                    id=doc.id,
                    file_name=doc.file_name,
                    content_type=doc.content_type,
                    project_id=doc.project_id,
                    storage_path=doc.storage_path,
                    name=doc.name,
                    description=doc.description,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                )
                for doc in orm
            ]
        else:
            return Document(
                id=orm.id,
                name=orm.name,
                file_name=orm.file_name,
                content_type=orm.content_type,
                project_id=orm.project_id,
                storage_path=orm.storage_path,
                description=orm.description,
                created_at=orm.created_at,
                updated_at=orm.updated_at,
            )

    def list_by_project(self, user_id: UUID, project_id: UUID) -> list[Document]:
        """List all Documents for a given project ID"""
        try:
            orm_documents = (
                self.db.query(DocumentORM)
                .join(DocumentORM.project)
                .filter(DocumentORM.project_id == project_id, ProjectORM.owner_id == user_id)
                .all()
            )

            return self._to_domain_entity(orm_documents)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def create(self, project_id: UUID, document: Document):
        """Persist the Document in the database"""
        # orm = DocumentORM(
        #     id=document.id,
        #     name=document.name,
        #     file_name=document.file_name,
        #     project_id=document.project_id,
        #     content_type=document.content_type,
        #     storage_path=document.storage_path,
        #     description=document.description,
        # )
        orm = DocumentORM(**document.__dict__)  # type: ignore

        try:
            self.db.add(orm)
            self.db.commit()
            self.db.refresh(orm)
            return self._to_domain_entity(orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e

    def get_by_filename(self, project_id: UUID, file_name: str) -> Document | None:
        """Get a document by its file name within a project"""
        try:
            orm_document = (
                self.db.query(DocumentORM)
                .filter(DocumentORM.project_id == project_id, DocumentORM.file_name == file_name)
                .first()
            )
            if orm_document:
                return self._to_domain_entity(orm_document)
            return None
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def save(self, document: Document):
        """Save changes to an existing document"""
        try:
            orm = self.db.query(DocumentORM).filter(DocumentORM.id == document.id).first()
            if not orm:
                raise DatabaseError(f"Document with ID {document.id} not found")

            orm.file_name = document.file_name
            orm.name = document.name
            orm.description = document.description
            orm.content_type = document.content_type
            orm.storage_path = document.storage_path
            orm.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(orm)
            return self._to_domain_entity(orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e

    def get_by_id(self, user_id: UUID, document_id: UUID) -> Document | None:
        """Get a document by its ID"""
        try:
            orm = (self.db.query(DocumentORM).join(DocumentORM.project)
                   .filter(DocumentORM.id == document_id, ProjectORM.owner_id == user_id)
                   .first())
            if orm is None:
                # I do not throw NotFound exception here but in service instead
                return None
            return self._to_domain_entity(orm)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def delete(self, document_id: UUID):
        """Delete a document by its ID"""
        try:
            orm = self.db.get(entity=DocumentORM, ident=document_id)
            if orm is None:
                raise DatabaseError(f"Document with ID {document_id} not found")

            self.db.delete(orm)
            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e
