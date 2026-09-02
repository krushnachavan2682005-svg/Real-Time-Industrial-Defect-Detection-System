import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import case, desc, func, text
from sqlalchemy.exc import SQLAlchemyError

from src.api.schemas import (
    BBox,
    DefectSchema,
    InspectionResponse,
    InspectionSummary,
    PLCDispatchInfo,
)
from src.persistence.exceptions import (
    InspectionPersistenceError,
)
from src.persistence.models import DefectModel, InspectionRecord
from src.persistence.repositories.inspection_repository import InspectionRepository
from src.persistence.schemas import InspectionHistoryItem

logger = logging.getLogger(__name__)


class SQLAlchemyInspectionRepository(InspectionRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(self, inspection: InspectionResponse, timestamp: datetime) -> None:
        try:
            with self.session_factory() as session:
                with session.begin():
                    record = InspectionRecord(
                        inspection_id=inspection.inspection_id,
                        timestamp=timestamp,
                        decision=inspection.decision,
                        severity=inspection.severity,
                        total_defects=inspection.summary.total_defects,
                        affected_classes=",".join(inspection.summary.affected_classes),
                        highest_confidence=0.0,  # We can calculate this if needed
                        pipeline_latency_ms=inspection.latency_ms,
                        plc_enabled=inspection.plc.enabled,
                        plc_dispatched=inspection.plc.dispatched,
                        plc_status=inspection.plc.status,
                        plc_message=inspection.plc.message,
                    )

                    max_conf = 0.0

                    for defect in inspection.defects:
                        if defect.confidence > max_conf:
                            max_conf = defect.confidence

                        # Simplified center calc
                        cx = (defect.bbox.x1 + defect.bbox.x2) // 2
                        cy = (defect.bbox.y1 + defect.bbox.y2) // 2
                        w = defect.bbox.x2 - defect.bbox.x1
                        h = defect.bbox.y2 - defect.bbox.y1
                        area = w * h

                        defect_record = DefectModel(
                            class_name=defect.class_name,
                            confidence=defect.confidence,
                            x1=defect.bbox.x1,
                            y1=defect.bbox.y1,
                            x2=defect.bbox.x2,
                            y2=defect.bbox.y2,
                            width=w,
                            height=h,
                            area=area,
                            center_x=cx,
                            center_y=cy,
                            region=defect.region,
                            inspection=record,
                        )
                        session.add(defect_record)

                    record.highest_confidence = max_conf
                    session.add(record)
        except SQLAlchemyError as e:
            logger.error(f"Failed to save inspection to database: {e}")
            raise InspectionPersistenceError("Failed to persist inspection.") from e

    def get_by_id(self, inspection_id: str) -> Optional[InspectionHistoryItem]:
        with self.session_factory() as session:
            record = (
                session.query(InspectionRecord)
                .filter(InspectionRecord.inspection_id == inspection_id)
                .first()
            )
            if not record:
                return None
            return self._map_to_history_item(record)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[InspectionHistoryItem], int]:
        with self.session_factory() as session:
            query = session.query(InspectionRecord)

            if filters:
                if "decision" in filters and filters["decision"]:
                    query = query.filter(
                        InspectionRecord.decision == filters["decision"]
                    )
                if "severity" in filters and filters["severity"]:
                    query = query.filter(
                        InspectionRecord.severity == filters["severity"]
                    )
                if "start_time" in filters and filters["start_time"]:
                    try:
                        st = datetime.fromisoformat(filters["start_time"])
                        query = query.filter(InspectionRecord.timestamp >= st)
                    except ValueError:
                        pass
                if "end_time" in filters and filters["end_time"]:
                    try:
                        et = datetime.fromisoformat(filters["end_time"])
                        query = query.filter(InspectionRecord.timestamp <= et)
                    except ValueError:
                        pass
                if "defect_class" in filters and filters["defect_class"]:
                    query = query.join(DefectModel).filter(
                        DefectModel.class_name == filters["defect_class"]
                    )

            total = query.count()

            # Default ordering: newest first
            query = query.order_by(desc(InspectionRecord.timestamp))

            # Pagination
            offset = (page - 1) * page_size
            records = query.offset(offset).limit(page_size).all()

            items = [self._map_to_history_item(record) for record in records]
            return items, total

    def health_check(self) -> bool:
        try:
            with self.session_factory() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def _map_to_history_item(self, record: InspectionRecord) -> InspectionHistoryItem:
        affected_classes = []
        if record.affected_classes:
            affected_classes = [
                c.strip() for c in record.affected_classes.split(",") if c.strip()
            ]

        summary = InspectionSummary(
            total_defects=record.total_defects, affected_classes=affected_classes
        )

        plc = PLCDispatchInfo(
            enabled=record.plc_enabled,
            dispatched=record.plc_dispatched,
            status=record.plc_status,
            message=record.plc_message,
        )

        defects = []
        for d in record.defects:
            defects.append(
                DefectSchema(
                    class_name=d.class_name,
                    confidence=d.confidence,
                    bbox=BBox(x1=d.x1, y1=d.y1, x2=d.x2, y2=d.y2),
                    region=d.region,
                )
            )

        return InspectionHistoryItem(
            inspection_id=record.inspection_id,
            decision=record.decision,
            severity=record.severity,
            summary=summary,
            defects=defects,
            latency_ms=record.pipeline_latency_ms,
            plc=plc,
            timestamp=record.timestamp,
        )

    def get_inspection_stats(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        with self.session_factory() as session:
            query = session.query(
                func.count(InspectionRecord.id).label("total_inspections"),
                func.sum(case((InspectionRecord.decision == "PASS", 1), else_=0)).label(
                    "pass_count"
                ),
                func.sum(
                    case((InspectionRecord.decision == "REVIEW", 1), else_=0)
                ).label("review_count"),
                func.sum(
                    case((InspectionRecord.decision == "REJECT", 1), else_=0)
                ).label("reject_count"),
                func.avg(InspectionRecord.total_defects).label("average_defects"),
                func.avg(InspectionRecord.pipeline_latency_ms).label("average_latency"),
            )

            if start_time:
                query = query.filter(InspectionRecord.timestamp >= start_time)
            if end_time:
                query = query.filter(InspectionRecord.timestamp <= end_time)

            result = query.one()

            return {
                "total_inspections": result.total_inspections or 0,
                "pass_count": int(result.pass_count or 0),
                "review_count": int(result.review_count or 0),
                "reject_count": int(result.reject_count or 0),
                "average_defects": float(result.average_defects or 0.0),
                "average_latency": float(result.average_latency or 0.0),
            }

    def get_defect_distribution(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        with self.session_factory() as session:
            query = session.query(
                DefectModel.class_name,
                func.count(DefectModel.id).label("total_occurrences"),
            ).join(InspectionRecord)

            if start_time:
                query = query.filter(InspectionRecord.timestamp >= start_time)
            if end_time:
                query = query.filter(InspectionRecord.timestamp <= end_time)

            query = query.group_by(DefectModel.class_name).order_by(
                desc("total_occurrences")
            )

            return [
                {
                    "class_name": row.class_name,
                    "total_occurrences": row.total_occurrences,
                }
                for row in query.all()
            ]

    def get_trends(
        self,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        with self.session_factory() as session:
            # We need a cross-DB way to group by time.
            # SQLite does not have date_trunc. We can use strftime for SQLite.
            # For this system using SQLite initially, we'll format timestamp to string.
            if interval == "hour":
                time_fmt = "%Y-%m-%dT%H:00:00Z"
            elif interval == "day":
                time_fmt = "%Y-%m-%dT00:00:00Z"
            elif interval == "week":
                # strftime week is %W or %U. We can just use date for week start?
                # For simplicity in sqlite, let's group by day if week is requested but we don't have standard cross DB week trunc.
                # Actually SQLite has no easy week trunc. Let's just do day.
                time_fmt = "%Y-%m-%dT00:00:00Z"
            else:
                time_fmt = "%Y-%m-%dT00:00:00Z"

            time_expr = func.strftime(time_fmt, InspectionRecord.timestamp)

            query = session.query(
                time_expr.label("bucket"),
                func.count(InspectionRecord.id).label("total_inspections"),
                func.sum(case((InspectionRecord.decision == "PASS", 1), else_=0)).label(
                    "pass_count"
                ),
                func.sum(
                    case((InspectionRecord.decision == "REVIEW", 1), else_=0)
                ).label("review_count"),
                func.sum(
                    case((InspectionRecord.decision == "REJECT", 1), else_=0)
                ).label("reject_count"),
            )

            if start_time:
                query = query.filter(InspectionRecord.timestamp >= start_time)
            if end_time:
                query = query.filter(InspectionRecord.timestamp <= end_time)

            query = query.group_by(time_expr).order_by(time_expr)

            results = []
            for row in query.all():
                if row.bucket:
                    # parse string back to datetime for pydantic
                    dt = datetime.strptime(row.bucket, time_fmt).replace(
                        tzinfo=timezone.utc
                    )
                    results.append(
                        {
                            "timestamp": dt,
                            "total_inspections": row.total_inspections,
                            "pass_count": int(row.pass_count or 0),
                            "review_count": int(row.review_count or 0),
                            "reject_count": int(row.reject_count or 0),
                        }
                    )
            return results
