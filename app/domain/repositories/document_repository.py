from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.enities.document import Document


class DocumentRepository(ABC):
    """A DocumentRepository interface"""

    @abstractmethod
    def list_by_project(self, user_id: UUID, project_id: UUID):
        """List all documents attached to the project"""
        pass

    def get_by_id(self, user_id: UUID, document_id: UUID) -> Document | None:
        """Get a document by its ID"""
        pass

    @abstractmethod
    def create(self, project_id: UUID, document: Document):
        pass

    @abstractmethod
    def save(self, document: Document):
        """Save changes to an existing document"""
        pass

    @abstractmethod
    def get_by_filename(self, project_id: UUID, file_name: str) -> Document | None:
        """Get a document by its file name within a project"""
        pass

    @abstractmethod
    def delete(self, document_id: UUID):
        """Delete a document by its ID"""
        pass
