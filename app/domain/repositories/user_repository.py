from abc import ABC, abstractmethod

from app.domain.enities.user import User


class UserRepository(ABC):
    """An abstract UserRepository interface"""

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass
