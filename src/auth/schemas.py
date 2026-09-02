from pydantic import BaseModel, Field

from src.auth.models import Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: int
    username: str
    role: Role
    is_active: bool


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ..., min_length=8
    )  # Configured by security.yaml but enforced here as a minimum
    role: Role
