from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.enities.project import Project


class ProjectRepository(ABC):
    """An abstract ProjectRepository interface"""

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[Project]:
        pass

    @abstractmethod
    def add(self, project: Project) -> Project:
        pass

    @abstractmethod
    def get_by_id(self, project_id: str) -> Optional[Project]:
        pass

    @abstractmethod
    def delete(self, project_id: str) -> bool:
        pass
