import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.enities.project import Project as DomainProject
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.orm.project_model import ProjectORM


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain_entity(orm: ProjectORM) -> DomainProject:
        """Map ORM model to domain model"""
        return DomainProject(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            owner=orm.owner_id,
            created_at=orm.created_at
        )

    def list_by_user(self, user_id: str) -> List[DomainProject]:
        orm_projects = self.db.query(ProjectORM).filter(ProjectORM.owner_id == user_id).all()
        return [self._to_domain_entity(orm) for orm in orm_projects]

    def add(self, project: DomainProject) -> DomainProject:
        orm = ProjectORM(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner
        )

        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain_entity(orm)

    def get_by_id(self, project_id: str) -> Optional[DomainProject]:
        orm = self.db.query(ProjectORM).filter(ProjectORM.id == project_id).first()
        return self._to_domain_entity(orm)

    def delete(self, project_id: str) -> bool:
        orm = self.db.query(ProjectORM).filter(ProjectORM.id == project_id).first()
        if not orm:
            return False
        self.db.delete(orm)
        self.db.commit()
        return True
