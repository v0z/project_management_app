from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError, UserWithEmailAlreadyExistsError)
from app.infrastructure.core.logger import logger
from app.routers.dependencies import get_auth_service, get_current_user
from app.routers.schemas.auth_schemas import (RegisterRequest, TokenResponse,
                                              UserOut, UserResponse)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/", summary="Register User", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(registration_data: RegisterRequest, auth_service=Depends(get_auth_service)):
    """Register a new user"""
    try:
        user = auth_service.register_user(
            username=registration_data.username, email=registration_data.email, password=registration_data.password
        )
        return UserResponse(id=user.id, username=user.username)
    except UserAlreadyExistsError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except UserWithEmailAlreadyExistsError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValidationError as e:
        logger.error(f"Validation error for {registration_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid registration data") from e
    except Exception as e:
        logger.error(f"Unexpected error for {registration_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(), auth_service=Depends(get_auth_service)
) -> TokenResponse:
    try:
        # the user service will generate a token on authentication success
        token = auth_service.authenticate(username=login_data.username, password=login_data.password)
        return TokenResponse(access_token=token)  # nosec B106
    except ValueError as e:
        logger.error(f"Failed authentication attempt for {login_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error for {login_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.get("/protected")
def protected_route(user: UserOut = Depends(get_current_user)):
    """TODO test endpoint remove later"""
    return {"msg": f"Hello {user.username}, you are authenticated!"}
