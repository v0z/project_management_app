from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.core.database import Base


class DocumentORM(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=True, default="")

    file_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    content_type: Mapped[str] = mapped_column(String(100), index=False, nullable=False)

    storage_path: Mapped[str] = mapped_column(String, index=False, nullable=False)

    description: Mapped[str] = mapped_column(String(300), index=False, nullable=True, default="")

    storage_backend: Mapped[str] = mapped_column(String(10), nullable=False, default="local")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now(UTC), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), default=None, nullable=True
    )

    project = relationship("ProjectORM", back_populates="documents")

    def __repr__(self):
        return f"<DocumentORM(id={self.id}, file_name={self.file_name}, content_type={self.content_type})>"
