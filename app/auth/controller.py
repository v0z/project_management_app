from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.model import RegisterUserRequest, Token, TokenData
from app.auth.service import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.logger import logger
from app.database.base import users_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenData, status_code=status.HTTP_201_CREATED)
def register(user: RegisterUserRequest):
    """Create a user"""
    if user.username in users_db:
        logger.warn(f"Attempt to create a user that already exist by: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    users_db[user.username] = hash_password(user.password)
    return TokenData(username=user.username)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Log-in a user"""
    hashed_pwd = users_db.get(form_data.username)
    if not hashed_pwd or not verify_password(form_data.password, hashed_pwd):
        # logger.warn(f'Invalid login attempt by: {form_data.username}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token, token_type="bearer")  # nosec B106


@router.get("/protected")
def protected_route(username: str = Depends(get_current_user)):
    """TODO test endpoint remove later"""
    logger.info(f"Access to a protected endpoint by {username}")
    return {"msg": f"Hello {username}, you are authenticated!"}


@router.get("/users")
def show_all():
    """TODO test endpoint remove later"""
    return {"users": users_db}
