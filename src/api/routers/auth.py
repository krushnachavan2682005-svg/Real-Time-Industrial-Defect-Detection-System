from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import get_auth_service, get_current_user, require_roles
from src.auth.models import AuthenticatedUser, Role
from src.auth.schemas import TokenResponse, UserCreateRequest, UserResponse
from src.auth.security import create_access_token
from src.auth.service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/auth/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "expires_in": 3600}


@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: AuthenticatedUser = Depends(get_current_user)):
    return current_user


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
def create_user(
    request: UserCreateRequest, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = auth_service.create_user(
            username=request.username, password=request.password, role=request.role
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/users",
    response_model=List[UserResponse],
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service),
):
    users_models = auth_service.user_repository.list_users(skip=skip, limit=limit)
    return [
        UserResponse(
            id=u.id, username=u.username, role=Role(u.role), is_active=u.is_active
        )
        for u in users_models
    ]
