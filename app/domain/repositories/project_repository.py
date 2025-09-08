from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.enities.project import Project
from app.domain.enities.user_project_role import UserProjectRole


class ProjectRepository(ABC):
    """An abstract ProjectRepository interface"""

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[Project]:
        """List all projects for a given user ID"""
        pass

    @abstractmethod
    def get_by_id(self, project_id: UUID) -> Project | None:
        """Get a project by its ID"""
        pass

    @abstractmethod
    def add(self, project: Project) -> Project:
        """Add a new project to the repository"""
        pass

    @abstractmethod
    def save(self, project: Project) -> Project:
        """Save changes to an existing project"""
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> bool:
        """Delete a project by its ID"""
        pass
