from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class User(BaseModel):
    """Domain representation of a user. Safe to pass around."""

    id: int
    username: str
    role: Role
    is_active: bool


class AuthenticatedUser(BaseModel):
    """Represents a verified current user."""

    id: int
    username: str
    role: Role
    is_active: bool
