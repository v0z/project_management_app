from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile


class DocumentStorage(ABC):
    """Abstract Document Storage"""

    @abstractmethod
    async def save(self, project_id: UUID, uploaded_file: UploadFile):
        pass

    @abstractmethod
    async def remove(self, storage_path: str):
        pass
