from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class DocumentSchema(BaseModel):
    id: UUID
    name: Optional[str] | None = None
    file_name: str
    project_id: UUID
    content_type: str
    storage_path: str
    description: Optional[str] | None = None
    created_at: datetime
    updated_at: Optional[datetime] | None = None

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
    name: Optional[str] | None = None
    description: Optional[str] | None = None



class DocumentFileUploadSchema(BaseModel):
    file_name: str
    storage_path: str

    model_config = ConfigDict(from_attributes=True)
