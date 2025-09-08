from uuid import UUID

from fastapi import HTTPException, status

from app.core.logger import logger
from app.domain.exceptions.project_exceptions import ProjectPermissionError


class DocumentNotFoundError(Exception):
    """Raised when a Document is not found"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Document not found: {self.message}")


class DocumentRetrieveError(Exception):
    """Raised when couldn't return Document"""

    def __init__(self, message: str):
        super().__init__(f"Document retrieval failed: {message}")
        self.message = message


class DocumentAccessError(Exception):
    """Raised when user has no rights to access Document"""

    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"User with ID: '{user_id}' has no rights to view this document")


class DocumentDeleteRightsError(Exception):
    """Raised when user has no rights to delete a Document"""

    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"User with ID: '{user_id}' has no rights to delete this document")


class DocumentCreateError(Exception):
    """Raised when couldn't create Document"""

    def __init__(self, message: str):
        super().__init__(f"Failed to create Document: {message}")
        self.message = message


class DocumentFileSaveError(Exception):
    """Raised when couldn't save Document on the filesystem"""

    def __init__(self, message: str):
        super().__init__(f"Failed to create Document: {message}")
        self.message = message


class DocumentFileDeleteError(Exception):
    """Raised when couldn't delete Document from the filesystem"""

    def __init__(self, message: str):
        super().__init__(f"Failed to delete Document: {message}")
        self.message = message


class DocumentDBDeleteError(Exception):
    """Raised when couldn't delete Document from the database"""

    def __init__(self, message: str):
        super().__init__(f"Failed to delete Document record: {message}")
        self.message = message


class DocumentUnsupportedStorageBackendError(Exception):
    """Raised when the document has unsupported storage backend"""

    def __init__(self, storage_backend: str):
        self.storage_backend = storage_backend
        super().__init__(f"Unsupported storage backend: {self.storage_backend}")

class DocumentUpdateEmptyError(Exception):
    """Raised when the document update has no changes"""

    def __init__(self):
        super().__init__("No changes in document")


async def document_exception_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except ProjectPermissionError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
        except DocumentFileSaveError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
        except DocumentCreateError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except DocumentRetrieveError as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e

        return result

    return wrapper
