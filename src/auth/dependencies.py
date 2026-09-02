from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.auth.models import AuthenticatedUser, Role
from src.auth.service import AuthService
from src.persistence.database import db
from src.persistence.repositories.user_repository import SQLAlchemyUserRepository

# We'll use the tokenUrl pointing to our login endpoint for swagger integration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_user_repository() -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db.get_session)


def get_auth_service(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = auth_service.get_current_user_from_token(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(*allowed_roles: Role):
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
            )
        return current_user

    return role_checker
