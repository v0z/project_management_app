from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    username: str
    email: EmailStr
    password: str
    password_confirmation: str

    @field_validator("password_confirmation")
    def passwords_match(cls, value, values):
        """Ensure password and password_confirmation fields match."""
        if values.data.get("password") != value:
            raise ValueError("Passwords do not match")
        return value

    """Strip whitespace from strings"""
    model_config = ConfigDict(str_strip_whitespace=True)


class LoginRequest(BaseModel):
    """Request model for logging in a user."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Response model for user details."""
    id: UUID
    username: str


class TokenResponse(BaseModel):
    """Response model for JWT token."""
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: str
    username: str

    model_config = ConfigDict(
        from_attributes=True
    )
