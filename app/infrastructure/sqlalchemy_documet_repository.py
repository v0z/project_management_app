from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.enities.document import Document
from app.domain.repositories.document_repository import DocumentRepository
from app.infrastructure.core.exceptions import DatabaseError
from app.infrastructure.orm import DocumentORM, ProjectORM, UserProjectRoleORM


class SQLAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def to_domain_entity(orm: DocumentORM | list[DocumentORM]) -> list[Document] | Document:
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
                    storage_backend=doc.storage_backend,
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
                storage_backend=orm.storage_backend,
            )

    def list_by_project(self, user_id: UUID, project_id: UUID) -> list[Document]:
        """List all Documents for a given project ID"""
        try:
            # show only if the current user is a participant of the project
            orm_documents = (
                self.db.query(DocumentORM)
                .join(DocumentORM.project)
                .filter(
                    DocumentORM.project_id == project_id,
                    ProjectORM.participants.any(UserProjectRoleORM.user_id == user_id),
                )
                .all()
            )

            return self.to_domain_entity(orm_documents)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def create(self, project_id: UUID, document: Document):
        """Persist the Document in the database"""
        orm = DocumentORM(**document.__dict__)  # type: ignore

        try:
            self.db.add(orm)
            self.db.commit()
            self.db.refresh(orm)
            return self.to_domain_entity(orm)
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
                return self.to_domain_entity(orm_document)
            return None
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def save(self, document: Document):
        """Save changes to an existing document"""
        try:
            orm = self.db.query(DocumentORM).filter(DocumentORM.id == document.id).first()
            if not orm:
                raise DatabaseError(f"Document with ID {document.id} not found")

            # dataclass
            data = vars(document)

            for key, value in data.items():
                if hasattr(orm, key):  # only update fields that exist in ORM
                    setattr(orm, key, value)

            # set update time
            orm.updated_at = datetime.now(UTC)

            self.db.commit()
            self.db.refresh(orm)
            return self.to_domain_entity(orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(str(e)) from e

    def get_by_id(
        self, user_id: UUID, document_id: UUID, to_orm=True
    ) -> None | list[Document] | Document | type[DocumentORM]:
        """Get a document by its ID"""
        try:
            orm = self.db.query(DocumentORM).filter(DocumentORM.id == document_id).first()

            if orm is None:
                # I do not throw NotFound exception here but in service instead
                return None
            if to_orm:
                return self.to_domain_entity(orm)
            return orm
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
