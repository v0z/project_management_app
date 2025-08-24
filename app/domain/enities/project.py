from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.enities.document import Document
from app.domain.exceptions.domain_exceptions import DomainValidationError


@dataclass
class Project:
    """Project entity"""

    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000

    id: UUID
    name: str
    description: str
    owner: UUID
    created_at: datetime
    documents: list[Document] = field(default_factory=list)

    def __post_init__(self):
        # validate after dataclass initializes fields
        self._validate_name(self.name)
        self._validate_description(self.description)

    def is_owned_by(self, user_id: UUID):
        """Check if the project is owned by the given user ID"""
        return self.owner == user_id

    @staticmethod
    def _validate_name(name: str):
        """Validate the project name"""
        if not name.strip():
            raise DomainValidationError("Project name cannot be empty")
        if len(name.strip()) > Project.MAX_NAME_LENGTH:
            raise DomainValidationError(f"Project name is too long, max {Project.MAX_NAME_LENGTH} characters")

    @staticmethod
    def _validate_description(description: str):
        """Validate the project description"""
        if description and len(description.strip()) > Project.MAX_DESCRIPTION_LENGTH:
            raise DomainValidationError(
                f"Project description is too long, max {Project.MAX_DESCRIPTION_LENGTH} characters"
            )

    def update(self, name: str | None = None, description: str | None = None):
        """Update project fields with validation"""
        if name is not None:
            self._validate_name(name=name)
            self.name = name
        if description is not None:
            self._validate_description(description=description)
            self.description = description
