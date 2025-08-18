from datetime import datetime, timezone
from uuid import uuid4, UUID

from app.domain.enities import Project, User
from app.domain.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    def add_project(self, name: str, description: str, user_id: UUID) -> Project:
        # name uniqueness is not enforced, so I don't check it

        project = Project(
            id=uuid4(),
            name=name,
            description=description,
            owner=user_id,
            created_at=datetime.now(timezone.utc)
        )
        return self.repo.add(project=project)
