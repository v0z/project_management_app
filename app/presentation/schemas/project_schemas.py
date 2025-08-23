from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class ProjectResponse(BaseModel):
    """A response model for Project"""

    id: UUID
    name: str
    description: str = None
    created_at: datetime

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
