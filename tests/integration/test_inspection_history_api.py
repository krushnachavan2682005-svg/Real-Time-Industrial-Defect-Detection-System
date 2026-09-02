import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.api.dependencies import app_state
from src.persistence.database import Database
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository
import yaml
import datetime
from src.api.schemas import InspectionResponse, InspectionSummary, PLCDispatchInfo

@pytest.fixture
def client(tmp_path):
    # Setup test DB
    db = Database()
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    db.initialize(db_url)
    
    from sqlalchemy import text
    with db.get_session() as session:
        session.execute(text("DELETE FROM defects"))
        session.execute(text("DELETE FROM inspections"))
        session.commit()
    
    # Init app state
    app_state.inspection_repository = SQLAlchemyInspectionRepository(db.get_session)
    
    # Mock configs for app startup to avoid breaking things
    app_state.config = {
        "api": {},
        "inference": {},
        "database": {"persistence": {"enabled": True, "url": db_url}}
    }
    
    app = create_app()
    
    # Mock authentication
    from src.auth.dependencies import get_current_user
    from src.auth.models import AuthenticatedUser, Role
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=1, username="testadmin", role=Role.ADMIN, is_active=True)
    
    with TestClient(app) as c:
        yield c, app_state.inspection_repository
        
    app.dependency_overrides.clear()

def test_get_history_empty(client):
    c, repo = client
    response = c.get("/api/v1/inspections")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data

def test_get_history_with_items(client):
    c, repo = client
    
    import uuid
    insp_id = uuid.uuid4().hex[:8]
    insp = InspectionResponse(
        inspection_id=insp_id,
        decision="PASS",
        severity="NONE",
        summary=InspectionSummary(total_defects=0, affected_classes=[]),
        defects=[],
        latency_ms=10.0,
        plc=PLCDispatchInfo(enabled=False, dispatched=False)
    )
    test_time = datetime.datetime.now(datetime.timezone.utc)
    repo.save(insp, test_time)
    
    response = c.get("/api/v1/inspections")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_get_inspection_by_id_not_found(client):
    c, _ = client
    response = c.get("/api/v1/inspections/999")
    assert response.status_code == 404

def test_health_check_with_db(client):
    c, _ = client
    response = c.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "healthy"
