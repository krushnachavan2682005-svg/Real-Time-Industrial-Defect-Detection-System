import pytest
from fastapi import HTTPException

from src.auth.dependencies import require_roles
from src.auth.models import AuthenticatedUser, Role


def test_require_roles_success():
    checker = require_roles(Role.ADMIN, Role.ENGINEER)

    admin_user = AuthenticatedUser(
        id=1, username="admin", role=Role.ADMIN, is_active=True
    )
    result = checker(current_user=admin_user)
    assert result == admin_user

    engineer_user = AuthenticatedUser(
        id=2, username="eng", role=Role.ENGINEER, is_active=True
    )
    result = checker(current_user=engineer_user)
    assert result == engineer_user


def test_require_roles_forbidden():
    checker = require_roles(Role.ADMIN)

    operator_user = AuthenticatedUser(
        id=3, username="op", role=Role.OPERATOR, is_active=True
    )

    with pytest.raises(HTTPException) as excinfo:
        checker(current_user=operator_user)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Operation not permitted"
