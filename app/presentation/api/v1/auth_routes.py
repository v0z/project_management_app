from fastapi import APIRouter, Depends, HTTPException, status
from app.presentation.dependencies import get_auth_service
from app.core.logger import logger

from app.presentation.schemas.auth_schemas import RegisterRequest, UserResponse

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserWithEmailAlreadyExistsError
from pydantic import ValidationError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/", summary="Register User", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(registration_data: RegisterRequest, auth_service=Depends(get_auth_service)):
    """Register a new user"""
    try:
        user = await auth_service.register_user(**registration_data.model_dump())
        return UserResponse(id=user.id, username=user.username)
    except UserAlreadyExistsError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UserWithEmailAlreadyExistsError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error for {registration_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid registration data")
    except Exception as e:
        logger.error(f"Unexpected error for {registration_data.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
