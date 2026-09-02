import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.persistence.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class InspectionRecord(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(String(36), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
    decision = Column(String(20), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    total_defects = Column(Integer, default=0, nullable=False)
    affected_classes = Column(String(255), nullable=True) # comma separated string
    highest_confidence = Column(Float, nullable=True)
    pipeline_latency_ms = Column(Float, nullable=False)
    
    plc_enabled = Column(Boolean, default=False, nullable=False)
    plc_dispatched = Column(Boolean, default=False, nullable=False)
    plc_status = Column(String(50), nullable=True)
    plc_message = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    defects = relationship("DefectModel", back_populates="inspection", cascade="all, delete-orphan")

class DefectModel(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    class_name = Column(String(100), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    
    x1 = Column(Integer, nullable=False)
    y1 = Column(Integer, nullable=False)
    x2 = Column(Integer, nullable=False)
    y2 = Column(Integer, nullable=False)
    
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    area = Column(Integer, nullable=False)
    
    center_x = Column(Integer, nullable=False)
    center_y = Column(Integer, nullable=False)
    
    region = Column(String(100), nullable=False)

    inspection = relationship("InspectionRecord", back_populates="defects")
