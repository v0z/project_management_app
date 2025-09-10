from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.enities.user_project_role import UserProjectRole
from app.domain.repositories.user_project_role_repository import \
    UserProjectRoleRepository
from app.infrastructure.core.exceptions import DatabaseError
from app.infrastructure.orm import UserProjectRoleORM


class SQLAlchemyUserProjectRoleRepository(UserProjectRoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, role_model: UserProjectRole) -> None:
        """Save the user role to the association table"""
        orm = UserProjectRoleORM(project_id=role_model.project_id, user_id=role_model.user_id, role=role_model.role)
        try:
            self.db.add(orm)
            self.db.commit()
            self.db.refresh(orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError from e

    def get_user_role_on_project(self, project_id: UUID, user_id: UUID) -> str:
        """Return a role, a given user has on a given project"""
        try:
            role = (
                self.db.query(UserProjectRoleORM.role)
                .filter(UserProjectRoleORM.project_id == project_id, UserProjectRoleORM.user_id == user_id)
                .scalar()
            )
            return role
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError from e
