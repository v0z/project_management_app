from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.services.auth_service import AuthService
from app.application.services.project_service import ProjectService
from app.core.security import decode_access_token
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.user_repository import UserRepository
from app.presentation.schemas.auth_schemas import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_repository() -> UserRepository:
    """provides a concrete UserRepository implementation which is wired in main.py"""
    raise NotImplementedError


def get_project_repository() -> ProjectRepository:
    """provides a concrete ProjectRepository implementation which is wired in main.py"""
    raise NotImplementedError


def get_auth_service() -> AuthService:
    """provides an auth service with a concrete UserRepository implementation"""
    raise NotImplementedError


def get_project_service() -> ProjectService:
    """provides a project service with a concrete ProjectRepository implementation"""
    return NotImplementedError


def get_current_user(
    token: str = Depends(oauth2_scheme), user_repository: UserRepository = Depends(get_user_repository)
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise credentials_exception

        user = user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # to not send password hash to api
        return UserOut(id=user.id, username=user.username, email=user.email)
        # return user
    except Exception as e:
        raise credentials_exception from e
