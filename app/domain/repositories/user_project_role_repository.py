from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.enities.user_project_role import UserProjectRole


class UserProjectRoleRepository(ABC):
    @abstractmethod
    def add(self, role_model: UserProjectRole) -> None:
        pass

    @abstractmethod
    def get_user_role_on_project(self, project_id: UUID, user_id: UUID) -> str:
        pass
