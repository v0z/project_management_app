from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.exceptions.domain_exceptions import DomainValidationError


@dataclass
class Document:
    """Document entity"""

    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 300

    id: UUID
    file_name: str
    project_id: UUID
    content_type: str
    storage_path: str
    created_at: datetime
    storage_backend: str
    updated_at: datetime | None = None
    name: str | None = ""
    description: str | None = ""

    @staticmethod
    def _validate_name(name: str):
        """Validate the document name"""
        if len(name.strip()) > Document.MAX_NAME_LENGTH:
            raise DomainValidationError(f"Project name is too long, max {Document.MAX_NAME_LENGTH} characters")

    @staticmethod
    def _validate_description(description: str):
        """Validate the document description"""
        if description and len(description.strip()) > Document.MAX_DESCRIPTION_LENGTH:
            raise DomainValidationError(
                f"Document description is too long, max {Document.MAX_DESCRIPTION_LENGTH} characters allowed"
            )

    def update(self, name: str | None = None, description: str | None = None):
        """Update document fields with validation"""
        if name is not None:
            self._validate_name(name=name)
            self.name = name
        if description is not None:
            self._validate_description(description=description)
            self.description = description
