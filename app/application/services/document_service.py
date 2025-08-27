from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.core.exceptions import DatabaseError
from app.core.logger import logger
from app.domain.enities.document import Document
from app.domain.exceptions.document_exceptions import (
    DocumentCreateError,
    DocumentDBDeleteError,
    DocumentFileDeleteError,
    DocumentFileSaveError,
    DocumentRetrieveError,
)
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.storage.document_storage import DocumentStorage
from app.presentation.schemas.document_schemas import DocumentDetailSchema

# Create storage once and reuse
# storage = FileSystemDocumentStorage()
# storage = S3DocumentStorage()


class DocumentService:
    def __init__(self, repo: DocumentRepository, storage: DocumentStorage):
        self.repo = repo
        self.storage = storage

    def list_documents(self, user_id: UUID, project_id: UUID):
        try:
            return self.repo.list_by_project(user_id=user_id, project_id=project_id)
        except DatabaseError as e:
            raise DocumentRetrieveError(str(e)) from e

    def save_to_file(self, project_id: UUID, uploaded_file: UploadFile) -> tuple:
        """Save the uploaded file to the filesystem and return its metadata"""
        try:
            return self.storage.save(project_id=project_id, uploaded_file=uploaded_file)
        except Exception as e:
            logger.error(e)
            raise DocumentFileSaveError(f"Failed to save file: {str(e)}") from e

    @staticmethod
    def delete_file(storage_path: str) -> None:
        """Delete a file from the filesystem given its storage path"""
        try:
            file_path = Path(storage_path)
            if file_path.exists():
                file_path.unlink()  # delete the file
            else:
                logger.warning(f"File at {storage_path} does not exist.")
        except Exception as e:
            logger.error(e)
            raise DocumentFileDeleteError(str(e)) from e

    async def upload_document(self, project_id: UUID, file_to_upload: UploadFile, details: dict[str]) -> Document:
        """Handle the upload of a document, saving it to the filesystem and database"""

        try:
            # save file to folder
            file_name, content_type, storage_path, storage_backend = await self.save_to_file(
                project_id=project_id, uploaded_file=file_to_upload
            )

        except Exception as e:
            logger.error(e)
            raise DocumentFileSaveError(str(e)) from e

        # check if document with the same name already exists in the project
        existing_document = self.repo.get_by_filename(project_id=project_id, file_name=file_name)

        if existing_document:
            # file already overwritten in save_to_file

            # update content type and path if changed
            existing_document.content_type = content_type
            existing_document.storage_path = storage_path
            existing_document.storage_backend = storage_backend

            # update other details
            existing_document.name = details.get("name", existing_document.name)
            existing_document.description = details.get("description", existing_document.description)

            # save changes to the database
            try:
                return self.repo.save(document=existing_document)
            except DatabaseError as e:
                logger.error(e)
                raise DocumentCreateError(str(e)) from e
        else:
            # create a new document record
            document = Document(
                id=uuid4(),
                file_name=file_name,
                project_id=project_id,
                content_type=content_type,
                storage_path=storage_path,
                storage_backend=storage_backend,
                name=details.get("name", ""),
                description=details.get("description", ""),
                created_at=datetime.now(UTC),
            )
            try:
                return self.repo.create(project_id=project_id, document=document)
            except DatabaseError as e:
                logger.error(e)
                raise DocumentCreateError(str(e)) from e

    async def delete_document(self, user_id: UUID, document_id: UUID):
        """Delete a document by its ID"""

        # TODO: check if the document belongs to the user

        document = self.repo.get_by_id(user_id=user_id, document_id=document_id)
        if not document:
            raise DocumentRetrieveError(f"Document with ID {document_id} not found")

        try:
            # delete from the database
            self.repo.delete(document_id=document_id)

        except DatabaseError as e:
            raise DocumentDBDeleteError(str(e)) from e

        else:
            # if successfully deleted from DB, delete the file from filesystem
            try:
                # self.delete_file(storage_path=document.storage_path)
                await self.storage.remove(storage_path=document.storage_path)

            except DocumentFileDeleteError as e:
                logger.error(f"Failed to delete file for document {document_id}: {str(e)}")

    def get_document(self, user_id: UUID, document_id: UUID) -> Document:
        """Retrieve a document by its ID"""
        document = self.repo.get_by_id(user_id=user_id, document_id=document_id)

        if not document:
            raise DocumentRetrieveError(f"Document with ID {document_id} not found")

        # convert to Pydantic schema for response
        return document

    def update_document(self, user_id: UUID, document_id: UUID, data: DocumentDetailSchema) -> Document:
        """Update document details"""
        document = self.repo.get_by_id(user_id=user_id, document_id=document_id)
        if not document:
            raise DocumentRetrieveError(f"Document with ID {document_id} not found")

        # pass them as keyword arguments to update()
        document.update(**data.model_dump(exclude_unset=True))

        try:
            # save the changes
            return self.repo.save(document)
        except DatabaseError as e:
            raise DocumentCreateError(str(e)) from e
