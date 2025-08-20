import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.infrastructure.orm import *


class UserORM(Base):
	"""ORM model for User entity."""

	__tablename__ = "users"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	username: Mapped[str] = mapped_column(
		String(50),
		unique=True,
		index=True,
		nullable=False,
	)
	email: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		index=True,
		nullable=False,
	)
	password_hash: Mapped[str] = mapped_column(
		String,
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		default=datetime.utcnow,
		nullable=False,
	)

	projects: Mapped[list["ProjectORM"]] = relationship(
		"ProjectORM", back_populates="owner", cascade="all, delete-orphan"
	)

	def __repr__(self):
		return f"<UserORM(id={self.id}, username={self.username}, email={self.email})>"
