import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.auth.security import hash_password
from src.persistence.database import Base, db
from src.persistence.models import UserModel


@pytest.fixture(scope="module")
def test_app():
    # Setup test database
    db.initialize("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=db.engine)

    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)

    # Create test users
    with db.get_session() as session:
        admin = UserModel(
            username="admin", password_hash=hash_password("adminpass"), role="ADMIN"
        )
        engineer = UserModel(
            username="engineer", password_hash=hash_password("engpass"), role="ENGINEER"
        )
        operator = UserModel(
            username="operator", password_hash=hash_password("oppass"), role="OPERATOR"
        )
        viewer = UserModel(
            username="viewer", password_hash=hash_password("viewpass"), role="VIEWER"
        )
        session.add_all([admin, engineer, operator, viewer])
        session.commit()


def test_login_success(test_app):
    response = test_app.post(
        "/api/v1/auth/login", data={"username": "admin", "password": "adminpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(test_app):
    response = test_app.post(
        "/api/v1/auth/login", data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

    response = test_app.post(
        "/api/v1/auth/login", data={"username": "unknown", "password": "password"}
    )
    assert response.status_code == 401


def test_get_me(test_app):
    # Login to get token
    login_res = test_app.post(
        "/api/v1/auth/login", data={"username": "engineer", "password": "engpass"}
    )
    token = login_res.json()["access_token"]

    response = test_app.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "engineer"
    assert data["role"] == "ENGINEER"


def test_get_me_no_token(test_app):
    response = test_app.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_rbac_user_management(test_app):
    # Login as admin
    admin_login = test_app.post(
        "/api/v1/auth/login", data={"username": "admin", "password": "adminpass"}
    )
    admin_token = admin_login.json()["access_token"]

    # Admin can list users
    res = test_app.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert len(res.json()) >= 4

    # Login as engineer
    eng_login = test_app.post(
        "/api/v1/auth/login", data={"username": "engineer", "password": "engpass"}
    )
    eng_token = eng_login.json()["access_token"]

    # Engineer cannot list users
    res = test_app.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {eng_token}"}
    )
    assert res.status_code == 403


def test_rbac_analytics(test_app):
    # Engineer can access analytics
    eng_login = test_app.post(
        "/api/v1/auth/login", data={"username": "engineer", "password": "engpass"}
    )
    eng_token = eng_login.json()["access_token"]

    # Engineer should succeed
    res = test_app.get(
        "/api/v1/analytics/summary", headers={"Authorization": f"Bearer {eng_token}"}
    )
    assert res.status_code == 200

    # Operator cannot access analytics
    op_login = test_app.post(
        "/api/v1/auth/login", data={"username": "operator", "password": "oppass"}
    )
    op_token = op_login.json()["access_token"]

    res = test_app.get(
        "/api/v1/analytics/summary", headers={"Authorization": f"Bearer {op_token}"}
    )
    assert res.status_code == 403
