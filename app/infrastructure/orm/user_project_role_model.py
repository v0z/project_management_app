import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (UUID, Column, DateTime, Enum, ForeignKey, String,
                        UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectRoleEnum(enum.Enum):
    """Two main roles for project members"""

    OWNER = "owner"
    PARTICIPANT = "participant"


class UserProjectRoleORM(Base):
    """Describes the role a user has in a given project"""

    __tablename__ = "user_project_roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # I tried Enum, but Sqlalchemy won this fight...
    role: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "project_id", name="unique_user_project"),)

    user = relationship("UserORM", back_populates="project_roles")
    project = relationship("ProjectORM", back_populates="participants")
