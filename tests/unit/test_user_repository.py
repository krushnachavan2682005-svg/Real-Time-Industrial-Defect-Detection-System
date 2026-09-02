import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.persistence.models import Base
from src.persistence.repositories.user_repository import SQLAlchemyUserRepository


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def test_create_and_get_user(session_factory):
    repo = SQLAlchemyUserRepository(session_factory)

    # Create
    user = repo.create_user(username="testuser", password_hash="hash", role="ENGINEER")
    assert user.id is not None
    assert user.username == "testuser"
    assert user.role == "ENGINEER"

    # Get by username
    retrieved = repo.get_by_username("testuser")
    assert retrieved is not None
    assert retrieved.id == user.id

    # Get by id
    retrieved_by_id = repo.get_by_id(user.id)
    assert retrieved_by_id is not None
    assert retrieved_by_id.username == "testuser"


def test_list_users(session_factory):
    repo = SQLAlchemyUserRepository(session_factory)
    repo.create_user(username="user1", password_hash="hash1", role="ADMIN")
    repo.create_user(username="user2", password_hash="hash2", role="VIEWER")

    users = repo.list_users()
    assert len(users) == 2
    assert users[0].username == "user1"
    assert users[1].username == "user2"
