from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.core.database import get_db
from app.infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """provides an auth service with a concrete UserRepository implementation"""
    repo = SQLAlchemyUserRepository(db)
    return AuthService(repo)