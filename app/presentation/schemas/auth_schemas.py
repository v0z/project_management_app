from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Request model for registering a user."""
    username: str
    email: EmailStr
    password: str


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
    token_type: str
