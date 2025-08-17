from abc import ABC, abstractmethod
from typing import Optional
from app.domain.enities.user import User


class UserRepository(ABC):
    """An abstract UserRepository interface"""

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass
