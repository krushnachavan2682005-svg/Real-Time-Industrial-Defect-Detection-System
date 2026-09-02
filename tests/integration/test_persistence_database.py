import pytest
import datetime
from src.persistence.database import Database
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository
from src.api.schemas import InspectionResponse, InspectionSummary, DefectSchema, BBox, PLCDispatchInfo

@pytest.fixture
def repo(tmp_path):
    db = Database()
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    db.initialize(db_url)
    return SQLAlchemyInspectionRepository(db.get_session)

def test_save_and_retrieve_inspection(repo):
    insp_id = "test-123"
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    response = InspectionResponse(
        inspection_id=insp_id,
        decision="REJECT",
        severity="HIGH",
        summary=InspectionSummary(total_defects=1, affected_classes=["scratch"]),
        defects=[
            DefectSchema(
                class_name="scratch",
                confidence=0.95,
                bbox=BBox(x1=10, y1=10, x2=50, y2=50),
                region="center"
            )
        ],
        latency_ms=105.0,
        plc=PLCDispatchInfo(enabled=True, dispatched=True, status="SUCCESS", message="Rejected")
    )
    
    repo.save(response, timestamp)
    
    item = repo.get_by_id(insp_id)
    assert item is not None
    assert item.inspection_id == insp_id
    assert item.decision == "REJECT"
    assert item.severity == "HIGH"
    assert len(item.defects) == 1
    assert item.defects[0].class_name == "scratch"

def test_list_inspections(repo):
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    for i in range(3):
        response = InspectionResponse(
            inspection_id=f"test-{i}",
            decision="PASS" if i % 2 == 0 else "REJECT",
            severity="NONE",
            summary=InspectionSummary(total_defects=0, affected_classes=[]),
            defects=[],
            latency_ms=10.0,
            plc=PLCDispatchInfo(enabled=False, dispatched=False)
        )
        repo.save(response, timestamp)
        
    items, total = repo.list(page=1, page_size=10)
    assert total == 3
    assert len(items) == 3
    
    items, total = repo.list(page=1, page_size=10, filters={"decision": "REJECT"})
    assert total == 1
    assert len(items) == 1
