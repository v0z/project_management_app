from uuid import UUID

from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)

from app.domain.exceptions.document_exceptions import (
    DocumentAccessError, DocumentCreateError, DocumentFileSaveError,
    DocumentRetrieveError, DocumentUnsupportedStorageBackendError,
    DocumentUpdateEmptyError)
from app.domain.exceptions.project_exceptions import ProjectPermissionError
from app.infrastructure.core.config import settings
from app.infrastructure.core.logger import logger
from app.routers.dependencies import get_current_user, get_document_service
from app.routers.schemas.auth_schemas import UserOut
from app.routers.schemas.document_schemas import (DocumentDetailSchema,
                                                  DocumentSchema)
from app.services import DocumentService

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentSchema], status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/", response_model=DocumentSchema)
async def upload_document(
    project_id: UUID,
    uploaded_file: UploadFile,
    service: DocumentService = Depends(get_document_service),
    name: str | None = Form(
        default=None, max_length=100, description="Optional name for the document", title="Document Name"
    ),
    description: str | None = Form(
        default=None, max_length=300, description="Optional description", title="Document Description"
    ),
    current_user: UserOut = Depends(get_current_user),
):
    # no file is selected for upload
    if not uploaded_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file was uploaded")

    max_file_size: int = 1024 * 1024 * settings.max_file_size  # mb to bytes
    allowed_types: list = settings.allowed_types

    # restrict allowed content types
    if uploaded_file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")

    # restrict file size
    if uploaded_file.size > max_file_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    details = {"name": name if name else None, "description": description if description else None}

    try:
        # upload the document
        return await service.upload_document(
            project_id=project_id, user_id=current_user.id, file_to_upload=uploaded_file, details=details
        )
    except ProjectPermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except DocumentFileSaveError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except DocumentCreateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.get("/{document_id}", status_code=status.HTTP_200_OK)
async def download_document(
    document_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Get a single document by its ID and return the file"""
    try:
        # depending on storage will return a FileResponse or a StreamingResponse
        return await service.download_document(user_id=current_user.id, document_id=document_id)
    except DocumentRetrieveError as e:
        logger.warning(f"Document not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DocumentAccessError as e:
        logger.warning(f"Unauthorized access: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except DocumentUnsupportedStorageBackendError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error while downloading {document_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e


@router.patch("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: UUID,
    name: str | None = Form(default=None, max_length=100, description="Optional name for the document", title="Document Name"),
    description: str | None = Form(default=None, max_length=300, description="Optional description", title="Document Description"),
    file: UploadFile | str = File(default=None, description="Optional update file"),
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Update document details like name and description"""
    try:
        updates = DocumentDetailSchema()
        if name is not None:
            updates.name = name
        if description is not None:
            updates.description = description

        return await service.update_document(user_id=current_user.id, document_id=document_id, data=updates,  uploaded_file=file)
    except DocumentAccessError as e:
        logger.warning(f"Unauthorized access: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except DocumentUpdateEmptyError as e:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail=str(e)) from e
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Delete a document by its ID"""
    try:
        await service.delete_document(user_id=current_user.id, document_id=document_id)
        # instead HTTP_204_NO_CONTENT, return an informative response
        return {"message": f"Document with ID: {document_id} was successfully deleted"}
    except DocumentRetrieveError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
