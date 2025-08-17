from datetime import datetime, timedelta, timezone

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from app.core.config import Settings

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, secret_key: str = settings.token_secret_key) -> str:
    """ Creates an access token based on user_id """
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(settings.token_expire_minutes))
    jwt_payload = {"sub": user_id, "exp": expire}
    try:
        return jwt.encode(jwt_payload, secret_key, algorithm=settings.token_algorithm)
    except PyJWTError:
        raise


def decode_access_token(token, secret_key: str = settings.token_secret_key) -> dict:
    """ Decodes the access token and returns its payload as a dict """
    try:
        return jwt.decode(token, secret_key, algorithms=[settings.token_algorithm])
    except PyJWTError:
        raise
