from uuid import uuid4

from app.domain.enities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserWithEmailAlreadyExistsError


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register_user(self, username: str, email: str, password: str) -> User:
        if self.repo.get_by_username(username=username):
            raise UserAlreadyExistsError(username=username)

        if self.repo.get_by_email(email=email):
            raise UserWithEmailAlreadyExistsError(email=email)

        user = User(
            id=uuid4(),
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        return self.repo.create(user)

    def login_user(self, username: str, password: str) -> str:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(
                plain_password=password, hashed_password=user.password_hash
        ):
            raise ValueError("Invalid credentials")
        return create_access_token(user_id=user.id)
