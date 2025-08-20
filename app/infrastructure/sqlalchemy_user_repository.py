from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enities.user import User as DomainUser
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.orm.user_model import UserORM


class SQLAlchemyUserRepository(UserRepository):
	def __init__(self, db: Session):
		self.db = db

	@staticmethod
	def _to_domain_entity(orm: UserORM) -> DomainUser:
		"""a mapping between orm and a domain model"""
		return DomainUser(
			id=orm.id,
			username=orm.username,
			email=orm.email,
			password_hash=orm.password_hash,
		)

	def get_by_id(self, user_id: str) -> Optional[DomainUser]:
		orm = self.db.query(UserORM).filter(UserORM.id == user_id).first()
		if not orm:
			return None
		return self._to_domain_entity(orm)

	def get_by_username(self, username: str) -> Optional[DomainUser]:
		orm = self.db.query(UserORM).filter(UserORM.username == username).first()
		if not orm:
			return None
		return self._to_domain_entity(orm)

	def get_by_email(self, email: str) -> Optional[DomainUser]:
		orm = self.db.query(UserORM).filter(UserORM.email == email).first()
		if not orm:
			return None
		return self._to_domain_entity(orm)

	def create(self, user: DomainUser) -> DomainUser:
		orm = UserORM(
			id=user.id,
			username=user.username,
			email=user.email,
			password_hash=user.password_hash,
		)

		self.db.add(orm)
		self.db.commit()
		self.db.refresh(orm)
		return self._to_domain_entity(orm)
