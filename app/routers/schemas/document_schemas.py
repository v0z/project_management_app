from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class DocumentSchema(BaseModel):
    id: UUID
    name: str | None | None = None
    file_name: str
    project_id: UUID
    content_type: str
    storage_path: str
    description: str | None | None = None
    created_at: datetime
    updated_at: datetime | None | None = None
    storage_backend: str

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime | None) -> str | None:
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None


class DocumentDetailSchema(BaseModel):
    name: str | None | None = None
    description: str | None | None = None


class DocumentFileUploadSchema(BaseModel):
    file_name: str
    storage_path: str

    model_config = ConfigDict(from_attributes=True)
