from pydantic import BaseModel, EmailStr, validator, field_validator, ConfigDict


class RegisterUserRequest(BaseModel):
    """Request model for user registration."""

    username: str
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


class Token(BaseModel):
    """Response model for JWT token."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data model for token payload."""

    username: str | None = None
