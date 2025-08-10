import os
from datetime import timedelta, datetime, timezone

import jwt
import pytest
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

from app.auth.service import hash_password, verify_password, create_access_token, get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""" happy path testing """


@pytest.fixture(scope='module')
def token_secret_key():
    """Provide the TOKEN_SECRET_KEY constant for tests."""
    return os.getenv("TOKEN_SECRET_KEY")


@pytest.fixture
def token_expire_minutes(scope='module'):
    """Provide the TOKEN_EXPIRE_MINUTES constant for tests."""
    return float(os.getenv("TOKEN_EXPIRE_MINUTES", 30))


# arrange
# act
# assert

def test_hash_password():
    """ bcrypt hashes will always be different even for the same password,
    because bcrypt automatically generates a new random salt every time you hash.
    We can verify the password against the hash using pwd_context.verify() """
    plain_password = "password"
    hashed_password = hash_password(plain_password)
    result = pwd_context.verify(plain_password, hashed_password)
    assert result is True


def test_verify_password():
    plain_password = "password1"
    hashed_password = hash_password(plain_password)
    result = verify_password(plain_password, hashed_password)
    assert result is True


def test_create_access_token(token_secret_key, token_expire_minutes):
    token_key = token_secret_key
    token_expiration = token_expire_minutes
    test_data = {"sub": "test"}
    test_expire = datetime.now(timezone.utc) + timedelta(minutes=token_expiration)
    result_token = create_access_token(test_data)
    result = jwt.decode(jwt=result_token, key=token_key, algorithms=["HS256"])
    # The token contains the correct subject
    assert result.get("sub") == "test"
    # The token's expiration is within the expected
    assert result.get("exp") <= int(test_expire.timestamp())


# def test_get_current_user():
#     pass
