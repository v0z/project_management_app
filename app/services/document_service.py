from collections.abc import Coroutine
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from black import timezone
from fastapi import UploadFile
from starlette.responses import FileResponse, StreamingResponse

from app.domain.enities.document import Document
from app.domain.enities.user_project_role import RoleEnum
from app.domain.exceptions.document_exceptions import (
    DocumentAccessError, DocumentCreateError, DocumentDBDeleteError,
    DocumentDeleteRightsError, DocumentFileDeleteError, DocumentFileSaveError,
    DocumentRetrieveError, DocumentUnsupportedStorageBackendError,
    DocumentUpdateEmptyError)
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.storage.document_storage import DocumentStorage
from app.infrastructure.core.exceptions import DatabaseError
from app.infrastructure.core.logger import logger
from app.infrastructure.orm import DocumentORM
from app.routers.schemas.document_schemas import DocumentDetailSchema
from app.services.project_service import ProjectService


class DocumentService:
    def __init__(self, repo: DocumentRepository, storage: DocumentStorage, project_service: ProjectService):
        self.repo = repo
        self.storage = storage
        self.project_service = project_service

    def list_documents(self, user_id: UUID, project_id: UUID):
        try:
            return self.repo.list_by_project(user_id=user_id, project_id=project_id)
        except DatabaseError as e:
            raise DocumentRetrieveError(str(e)) from e

    def upload_file(self, project_id: UUID, uploaded_file: UploadFile) -> Coroutine[Any, Any, Any]:
        """Save the uploaded file to the filesystem and return its metadata"""
        try:
            return self.storage.save(project_id=project_id, uploaded_file=uploaded_file)
        except Exception as e:
            logger.error(e)
            raise DocumentFileSaveError(f"Failed to save file: {str(e)}") from e

    async def upload_document(
        self, project_id: UUID, user_id: UUID, file_to_upload: UploadFile, details: dict[str, str]
    ) -> Document:
        """Handle the upload of a document, saving it to the filesystem and database"""

        # this will raise ProjectNotFoundError or ProjectPermissionError if user is not a participant
        self.project_service.get_project(project_id=project_id, user_id=user_id)

        # upload file and save to fs or cloud
        file_name, content_type, storage_path, storage_backend = await self.upload_file(
            project_id=project_id, uploaded_file=file_to_upload
        )

        # check if document with the same name already exists in the project
        existing_document = self.repo.get_by_filename(project_id=project_id, file_name=file_name)

        if existing_document:
            # file already overwritten in upload_file

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
                created_at=datetime.now(tz=timezone.utc),
            )
            try:
                return self.repo.create(project_id=project_id, document=document)
            except DatabaseError as e:
                logger.error(e)
                raise DocumentCreateError(str(e)) from e

    async def delete_document(self, user_id: UUID, document_id: UUID):
        """Delete a document by its ID"""

        # TODO: check the actual storage backend, from where to delete the file!!!

        #  here we get a document ORM model, not a domain model (by setting the 'to_orm' flag to false)
        document_orm: DocumentORM = self.repo.get_by_id(user_id=user_id, document_id=document_id, to_orm=False)

        if not document_orm:
            raise DocumentRetrieveError(f"document with ID '{document_id}' not found")

        # check if user trying to delete a document has owner rights on the project
        if not self.is_user_owner_in_document_project(document_orm=document_orm, user_id=user_id):
            raise DocumentDeleteRightsError(user_id=user_id)

        # convert to domain model
        document = self.repo.to_domain_entity(document_orm)

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

        #  here we get a document ORM model, not a domain model (by setting the 'to_orm' flag to false)
        document_orm: DocumentORM = self.repo.get_by_id(user_id=user_id, document_id=document_id, to_orm=False)

        if not document_orm:
            raise DocumentRetrieveError(f"document with ID '{document_id}' not found")

        # check if user is a participant on the project, to which the doc belongs to
        # almost all methods in this service will call get_document and thus this  check will verify,
        # that the user is a participant on the project this document belongs to
        if not self.is_user_participant_in_document_project(document_orm=document_orm, user_id=user_id):
            raise DocumentAccessError(user_id=user_id)

        # convert to Pydantic schema for response by calling the repo's static method
        return self.repo.to_domain_entity(document_orm)

    async def update_document(self, user_id: UUID, document_id: UUID, data: DocumentDetailSchema, uploaded_file: UploadFile | None = None) -> Document:
        """Update document details"""

        # Retrieve the existing document and check user access
        document = self.get_document(user_id=user_id, document_id=document_id)
        if not document:
            raise DocumentRetrieveError(f"Document with ID {document_id} not found")

        # need to filter out unset values because by default unset vals are passed as "" string
        # because data.model_dump(exclude_unset=True, exclude_none=True) - doesn't work and exclude_defaults=True - also
        update_data = {key: value for key, value in data.model_dump(exclude_unset=True).items() if value}

        if not update_data and not uploaded_file:
            raise DocumentUpdateEmptyError

        old_storage_path = document.storage_path
        new_document_data = {}

        # check if new file is being uploaded
        if uploaded_file:
            # upload new file and get new metadata
            new_file_name, new_content_type, new_storage_path, new_storage_backend = await self.upload_file(
                project_id=document.project_id, uploaded_file=uploaded_file
            )

            # prepare ew file details for update
            new_document_data = {
                "file_name": new_file_name,
                "content_type": new_content_type,
                "storage_path": new_storage_path,
                "storage_backend": new_storage_backend,
            }


        # update document with data from request
        document.update(updates={**update_data, **new_document_data})

        try:
            # save the changes to database
            updated_document =  self.repo.save(document)
        except DatabaseError as e:
            raise DocumentCreateError(str(e)) from e

        # delete old file
        if uploaded_file:
            try:
                await self.storage.remove(storage_path=old_storage_path)
            except Exception as e:
                logger.error(f"Error while trying to delete old file from document {document_id}: {str(e)}")


        return updated_document

    async def download_document(self, user_id: UUID, document_id: UUID):
        """Returns a FileResponse or StreamingResponse"""
        """
        The document's attribute "storage_backend" signifies, on which storage type the file is saved on.
        Based on this knowledge, we can get the file, from its actual storage, even if the current storage backend
        differs. e.g: we currently using s3, but previously the file was saved on a local fs, and it would be useless
        to search for the file on the s3.
        """
        document = self.get_document(user_id=user_id, document_id=document_id)
        match document.storage_backend:
            case "local":
                # open a local file
                return FileResponse(
                    path=document.storage_path, filename=document.file_name, media_type=document.content_type
                )
            case "s3":
                # get the s3 obj from storage
                s3_object = await self.storage.download(document.storage_path)
                headers = {
                    "Content-Disposition": f'attachment; filename="{document.file_name}"',
                    "Content-Length": str(s3_object.get("ContentLength")),
                    "Last-Modified": s3_object.get("LastModified").strftime("%a, %d %b %Y %H:%M:%S GMT"),
                }

                return StreamingResponse(
                    s3_object["Body"].iter_chunks(), media_type=document.content_type, headers=headers
                )
            case _:
                raise DocumentUnsupportedStorageBackendError(storage_backend=document.storage_backend)

    @staticmethod
    def is_user_participant_in_document_project(document_orm: DocumentORM, user_id: UUID) -> bool:
        """Check if user is a participant on the project, the document belongs to"""
        return any([p.user_id == user_id and p.role is not None for p in document_orm.project.participants])

    @staticmethod
    def is_user_owner_in_document_project(document_orm: DocumentORM, user_id: UUID) -> bool:
        """Check if given user has owner role on the project to which the document belongs to"""
        return any([p.user_id == user_id and p.role == RoleEnum.OWNER for p in document_orm.project.participants])
