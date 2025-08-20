import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.infrastructure.orm import *


class ProjectORM(Base):
	"""ORM model for Project entity."""

	__tablename__ = "projects"

	id: Mapped[UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	name: Mapped[str] = mapped_column(
		String(100),
		index=True,
		nullable=False,
	)
	description: Mapped[str] = mapped_column(
		String,
		nullable=True,
	)
	owner_id: Mapped[UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		default=datetime.utcnow,
		nullable=False,
	)

	owner: Mapped["UserORM"] = relationship("UserORM", back_populates="projects")

	def __repr__(self):
		return f"<ProjectORM(id={self.id}, name={self.name}, description={self.description})>"
