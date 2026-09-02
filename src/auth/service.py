from typing import Optional

from src.auth.models import AuthenticatedUser, Role, User
from src.auth.security import (
    decode_access_token,
    hash_password,
    verify_password,
)
from src.persistence.repositories.user_repository import SQLAlchemyUserRepository


class AuthService:
    def __init__(self, user_repository: SQLAlchemyUserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user_model = self.user_repository.get_by_username(username)
        if not user_model:
            return None
        if not verify_password(password, user_model.password_hash):
            return None
        if not user_model.is_active:
            return None

        return User(
            id=user_model.id,
            username=user_model.username,
            role=Role(user_model.role),
            is_active=user_model.is_active,
        )

    def create_user(self, username: str, password: str, role: Role) -> User:
        # Check if username exists
        existing_user = self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError(f"Username {username} already exists")

        hashed_password = hash_password(password)
        user_model = self.user_repository.create_user(
            username=username, password_hash=hashed_password, role=role.value
        )
        return User(
            id=user_model.id,
            username=user_model.username,
            role=Role(user_model.role),
            is_active=user_model.is_active,
        )

    def get_current_user_from_token(self, token: str) -> Optional[AuthenticatedUser]:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token payload")

        user_model = self.user_repository.get_by_username(username)
        if not user_model or not user_model.is_active:
            raise ValueError("User not found or inactive")

        return AuthenticatedUser(
            id=user_model.id,
            username=user_model.username,
            role=Role(user_model.role),
            is_active=user_model.is_active,
        )
