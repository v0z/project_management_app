import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()

# "database"
from app.database.base import users_db

# get env values
TOKEN_SECRET_KEY = os.getenv("TOKEN_SECRET_KEY", "should_use_a_random_string")
TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = float(os.getenv("TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise credentials_exception
    except PyJWTError:
        logger.error("Token decoding error")
        raise credentials_exception
    return username
