from unittest.mock import MagicMock

from src.auth.models import Role
from src.auth.security import create_access_token, hash_password
from src.auth.service import AuthService
from src.persistence.models import UserModel


def test_authenticate_user_success():
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = UserModel(
        id=1,
        username="admin",
        password_hash=hash_password("adminpass"),
        role="ADMIN",
        is_active=True,
    )
    service = AuthService(user_repository=mock_repo)
    user = service.authenticate_user("admin", "adminpass")

    assert user is not None
    assert user.username == "admin"
    assert user.role == Role.ADMIN


def test_authenticate_user_wrong_password():
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = UserModel(
        id=1,
        username="admin",
        password_hash=hash_password("adminpass"),
        role="ADMIN",
        is_active=True,
    )
    service = AuthService(user_repository=mock_repo)
    user = service.authenticate_user("admin", "wrongpass")

    assert user is None


def test_authenticate_user_not_found():
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = None
    service = AuthService(user_repository=mock_repo)
    user = service.authenticate_user("unknown", "pass")

    assert user is None


def test_get_current_user_from_token():
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = UserModel(
        id=1, username="admin", password_hash="hash", role="ADMIN", is_active=True
    )
    service = AuthService(user_repository=mock_repo)

    token = create_access_token(data={"sub": "admin"})
    user = service.get_current_user_from_token(token)

    assert user.username == "admin"
    assert user.role == Role.ADMIN
