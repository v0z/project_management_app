import uuid
import re
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form, Body
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse

from app.application.services.document_service import DocumentService
from app.core.logger import logger
from app.domain.enities.document import Document
from app.domain.exceptions.document_exceptions import DocumentRetrieveError, DocumentCreateError, DocumentFileSaveError
from app.presentation.dependencies import get_document_service, get_current_user
from app.presentation.schemas.auth_schemas import UserOut
from app.presentation.schemas.document_schemas import DocumentSchema, DocumentDetailSchema
import os

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentSchema], status_code=status.HTTP_200_OK)
async def list_documents(
    project_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Show all documents that belong to the project of an authenticated user"""
    try:
        return service.list_documents(user_id=current_user.id, project_id=project_id)
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from e


@router.post("/", response_model=DocumentSchema)
async def upload_document(
    project_id: UUID,
    uploaded_file: UploadFile,
    service: DocumentService = Depends(get_document_service),
    name: Optional[str] = Form(
        default=None, max_length=100, description="Optional name for the document", title="Document Name"),
    description: Optional[str] = Form(
        default=None, max_length=300, description="Optional description", title="Document Description"),
    use_cloud: bool = False,
):
    # no file is uploaded
    if not uploaded_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

    MAX_FILE_SIZE: int = 5 * 1024 * 1024

    # restrict allowed content types
    allowed_types = {"application/pdf", "image/png", "image/jpeg"}
    if uploaded_file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")

    # restrict file size
    if uploaded_file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    details = {
        "name": name if name else None,
        "description": description if description else None,
    }

    # save to folder
    if not use_cloud:
        try:
            # upload the document
            return service.upload_document(project_id=project_id, file_to_upload=uploaded_file, details=details)

        except DocumentFileSaveError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
        except DocumentCreateError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e) from e

    else:
        raise NotImplemented


@router.get("/{document_id}", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Get a single document by its ID and return the file"""
    try:
        document = service.get_document(user_id=current_user.id, document_id=document_id)
        # return the file as a response
        return FileResponse(path=document.storage_path, filename=document.file_name, media_type=document.content_type)
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from e


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Delete a document by its ID"""
    try:
        service.delete_document(user_id=current_user.id, document_id=document_id)
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from e

@router.patch("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: UUID, data: DocumentDetailSchema = Body(...),
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Update document details like name and description"""
    try:
        return service.update_document(user_id=current_user.id, document_id=document_id, data=data)
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e



