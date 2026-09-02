from datetime import datetime
from typing import Optional, List
from src.persistence.repositories.inspection_repository import InspectionRepository
from src.analytics.models import (
    AnalyticsSummary, 
    TimeRange, 
    InspectionStatistics, 
    DefectAnalytics, 
    TrendPoint
)
from src.analytics.aggregations import calculate_rates, generate_quality_alerts
from src.analytics.config import AnalyticsSettings
from src.core.exceptions import ApplicationError

class AnalyticsQueryError(ApplicationError):
    pass

class InvalidTimeRangeError(ApplicationError):
    pass

class AnalyticsService:
    def __init__(self, repository: InspectionRepository, config: AnalyticsSettings):
        self.repository = repository
        self.config = config

    def _validate_time_range(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> None:
        if start_time and end_time:
            if start_time > end_time:
                raise InvalidTimeRangeError("start_time cannot be after end_time")
            
            delta = end_time - start_time
            if delta.days > self.config.max_time_range_days:
                raise InvalidTimeRangeError(f"Time range exceeds maximum allowed days ({self.config.max_time_range_days})")

    def get_summary(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> AnalyticsSummary:
        self._validate_time_range(start_time, end_time)
        
        if not start_time:
            start_time = datetime.min
        if not end_time:
            end_time = datetime.max
            
        try:
            stats_raw = self.repository.get_inspection_stats(start_time, end_time)
            
            pass_rate, review_rate, reject_rate = calculate_rates(
                stats_raw["pass_count"], 
                stats_raw["review_count"], 
                stats_raw["reject_count"]
            )
            
            stats = InspectionStatistics(
                total_inspections=stats_raw["total_inspections"],
                pass_count=stats_raw["pass_count"],
                review_count=stats_raw["review_count"],
                reject_count=stats_raw["reject_count"],
                pass_rate=pass_rate,
                review_rate=review_rate,
                reject_rate=reject_rate,
                average_defects_per_inspection=stats_raw["average_defects"],
                average_latency_ms=stats_raw["average_latency"]
            )
            
            defect_dist_raw = self.repository.get_defect_distribution(start_time, end_time)
            defects = []
            total_defects = sum(d["total_occurrences"] for d in defect_dist_raw)
            for d in defect_dist_raw:
                pct = d["total_occurrences"] / total_defects if total_defects > 0 else 0.0
                defects.append(DefectAnalytics(
                    class_name=d["class_name"],
                    total_occurrences=d["total_occurrences"],
                    percentage=pct
                ))
                
            trends_raw = self.repository.get_trends(self.config.trend.default_interval, start_time, end_time)
            trends = []
            for t in trends_raw:
                _, _, t_reject = calculate_rates(t["pass_count"], t["review_count"], t["reject_count"])
                trends.append(TrendPoint(
                    timestamp=t["timestamp"],
                    total_inspections=t["total_inspections"],
                    pass_count=t["pass_count"],
                    review_count=t["review_count"],
                    reject_count=t["reject_count"],
                    reject_rate=t_reject
                ))
                
            alerts = generate_quality_alerts(stats, self.config)
            
            return AnalyticsSummary(
                time_range=TimeRange(start=start_time, end=end_time),
                inspection_statistics=stats,
                defect_distribution=defects,
                trends=trends,
                quality_alerts=alerts
            )
        except Exception as e:
            raise AnalyticsQueryError(f"Failed to generate analytics summary: {e}") from e

    def get_defect_distribution(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[DefectAnalytics]:
        self._validate_time_range(start_time, end_time)
        try:
            defect_dist_raw = self.repository.get_defect_distribution(start_time, end_time)
            defects = []
            total_defects = sum(d["total_occurrences"] for d in defect_dist_raw)
            for d in defect_dist_raw:
                pct = d["total_occurrences"] / total_defects if total_defects > 0 else 0.0
                defects.append(DefectAnalytics(
                    class_name=d["class_name"],
                    total_occurrences=d["total_occurrences"],
                    percentage=pct
                ))
            return defects
        except Exception as e:
            raise AnalyticsQueryError(f"Failed to generate defect distribution: {e}") from e

    def get_trends(self, interval: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[TrendPoint]:
        if interval not in ["hour", "day", "week"]:
            raise ApplicationError(f"Invalid interval: {interval}")
            
        self._validate_time_range(start_time, end_time)
        try:
            trends_raw = self.repository.get_trends(interval, start_time, end_time)
            trends = []
            for t in trends_raw:
                _, _, t_reject = calculate_rates(t["pass_count"], t["review_count"], t["reject_count"])
                trends.append(TrendPoint(
                    timestamp=t["timestamp"],
                    total_inspections=t["total_inspections"],
                    pass_count=t["pass_count"],
                    review_count=t["review_count"],
                    reject_count=t["reject_count"],
                    reject_rate=t_reject
                ))
            return trends
        except Exception as e:
            raise AnalyticsQueryError(f"Failed to generate trends: {e}") from e
