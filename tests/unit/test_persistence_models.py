import pytest
import datetime
from src.persistence.models import InspectionRecord, DefectModel

def test_inspection_record_model():
    record = InspectionRecord(
        inspection_id="1234",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        decision="PASS",
        severity="NONE",
        total_defects=0,
        pipeline_latency_ms=45.2,
        plc_enabled=False,
        plc_dispatched=False
    )
    assert record.inspection_id == "1234"
    assert record.decision == "PASS"

def test_defect_model():
    defect = DefectModel(
        class_name="scratch",
        confidence=0.9,
        x1=0, y1=0, x2=10, y2=10,
        width=10, height=10, area=100,
        center_x=5, center_y=5,
        region="top_left"
    )
    assert defect.class_name == "scratch"
    assert defect.confidence == 0.9
    assert defect.area == 100
