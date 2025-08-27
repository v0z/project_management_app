from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class DocumentSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """A response model for Project"""

    id: UUID
    name: str
    description: str = None
    owner: UUID
    created_at: datetime
    documents: list[DocumentSchema] = []

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class ProjectCreateRequest(BaseModel):
    """Request model for project creation."""

    name: str
    description: str | None = None

    """Strip whitespace from strings"""
    model_config = ConfigDict(str_strip_whitespace=True)


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
