from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.project_service import ProjectService
from app.core.database import get_db
from app.core.security import decode_access_token
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.sqlalchemy_project_repository import SQLAlchemyProjectRepository
from app.infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.presentation.schemas.auth_schemas import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_repository(db: Session = Depends(get_db)):
	"""sets a concrete UserRepository implementation"""
	return SQLAlchemyUserRepository(db)


def get_project_repository(db: Session = Depends(get_db)):
	"""sets a concrete UserRepository implementation"""
	return SQLAlchemyProjectRepository(db)


def get_auth_service(
	repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
	"""provides an auth service with a concrete UserRepository implementation"""
	return AuthService(repo)


def get_project_service(
	repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
	"""provides a project service with a concrete UserRepository implementation"""
	return ProjectService(repo)


def get_current_user(
	token: str = Depends(oauth2_scheme),
	user_repository: UserRepository = Depends(get_user_repository),
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
