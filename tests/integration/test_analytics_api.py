import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.api.dependencies import app_state
from src.persistence.database import Database
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository
import datetime
from src.api.schemas import InspectionResponse, InspectionSummary, PLCDispatchInfo, DefectSchema, BBox

@pytest.fixture
def client(tmp_path):
    db = Database()
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    db.initialize(db_url)
    
    from sqlalchemy import text
    with db.get_session() as session:
        session.execute(text("DELETE FROM defects"))
        session.execute(text("DELETE FROM inspections"))
        session.commit()
        
    repo = SQLAlchemyInspectionRepository(db.get_session)
    app_state.inspection_repository = repo
    app_state.config = {
        "api": {},
        "inference": {},
        "database": {"persistence": {"enabled": True, "url": db_url}}
    }
    
    app = create_app()
    with TestClient(app) as c:
        yield c, repo

def test_analytics_summary_empty(client):
    c, repo = client
    response = c.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "inspection_statistics" in data

def test_analytics_summary_with_data(client):
    c, repo = client
    
    import uuid
    insp_id = uuid.uuid4().hex[:8]
    insp = InspectionResponse(
        inspection_id=insp_id,
        decision="REJECT",
        severity="HIGH",
        summary=InspectionSummary(total_defects=1, affected_classes=["scratch"]),
        defects=[DefectSchema(class_name="scratch", confidence=0.9, bbox=BBox(x1=0,y1=0,x2=10,y2=10), region="C")],
        latency_ms=10.0,
        plc=PLCDispatchInfo(enabled=False, dispatched=False)
    )
    test_time = datetime.datetime.now(datetime.timezone.utc)
    repo.save(insp, test_time)
    response = c.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "inspection_statistics" in data
    assert "defect_distribution" in data

def test_analytics_invalid_interval(client):
    c, _ = client
    response = c.get("/api/v1/analytics/trends?interval=invalid")
    assert response.status_code == 400

def test_analytics_invalid_time_range(client):
    c, _ = client
    # start_time > end_time
    response = c.get("/api/v1/analytics/summary?start_time=2026-02-01T00:00:00&end_time=2026-01-01T00:00:00")
    assert response.status_code == 400
    assert "cannot be after end_time" in response.json()["detail"]
