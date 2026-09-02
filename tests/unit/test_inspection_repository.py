import pytest
from src.persistence.database import Database
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository

def test_repository_health_check_fail():
    db = Database()
    # Not initialized, should fail
    # We shouldn't use a live instance for real uninit test, but just mock the session factory
    class MockSessionFactory:
        def __call__(self):
            raise Exception("Mock connection error")
            
    repo = SQLAlchemyInspectionRepository(MockSessionFactory())
    assert not repo.health_check()
