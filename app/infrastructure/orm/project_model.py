import uuid
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.orm.user_model import UserORM
    from app.infrastructure.orm.user_project_role_model import \
        UserProjectRoleORM


class ProjectORM(Base):
    """ORM model for Project entity."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    owner_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now(UTC), nullable=False
    )

    # owner relationship
    owner: Mapped["UserORM"] = relationship("UserORM", back_populates="projects")  # noqa: F405

    # one-to-many relationship with documents
    documents = relationship("DocumentORM", back_populates="project", cascade="all, delete-orphan")

    # association with roles
    participants: Mapped[list["UserProjectRoleORM"]] = relationship(
        "UserProjectRoleORM", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ProjectORM(id={self.id}, name={self.name}, description={self.description})>"
