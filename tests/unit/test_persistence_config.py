import pytest
import yaml
from src.persistence.database import Database
from src.persistence.exceptions import DatabaseConnectionError

def test_database_initialization(tmp_path):
    db = Database()
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    
    db.initialize(db_url)
    assert db.engine is not None
    assert db.SessionLocal is not None

def test_database_invalid_config():
    db = Database()
    with pytest.raises(DatabaseConnectionError):
        db.initialize("invalid_url")
