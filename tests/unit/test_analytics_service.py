import pytest
from datetime import datetime, timezone, timedelta
from src.analytics.service import AnalyticsService, InvalidTimeRangeError
from src.analytics.config import AnalyticsSettings
from src.persistence.repositories.inspection_repository import InspectionRepository

class MockRepo(InspectionRepository):
    def save(self, *args, **kwargs): pass
    def get_by_id(self, *args, **kwargs): pass
    def list(self, *args, **kwargs): pass
    def health_check(self): return True
    
    def get_inspection_stats(self, *args, **kwargs):
        return {
            "total_inspections": 100,
            "pass_count": 80,
            "review_count": 10,
            "reject_count": 10,
            "average_defects": 1.2,
            "average_latency": 25.0
        }
    def get_defect_distribution(self, *args, **kwargs):
        return [
            {"class_name": "scratch", "total_occurrences": 60},
            {"class_name": "patch", "total_occurrences": 40}
        ]
    def get_trends(self, *args, **kwargs):
        return []

def test_analytics_service_summary():
    repo = MockRepo()
    config = AnalyticsSettings()
    service = AnalyticsService(repo, config)
    
    summary = service.get_summary()
    assert summary.inspection_statistics.total_inspections == 100
    assert summary.inspection_statistics.pass_rate == 0.8
    
    assert len(summary.defect_distribution) == 2
    assert summary.defect_distribution[0].class_name == "scratch"
    assert summary.defect_distribution[0].percentage == 0.6
    
def test_analytics_service_time_validation():
    repo = MockRepo()
    config = AnalyticsSettings(max_time_range_days=30)
    service = AnalyticsService(repo, config)
    
    now = datetime.now(timezone.utc)
    # End before start
    with pytest.raises(InvalidTimeRangeError):
        service.get_summary(now, now - timedelta(days=1))
        
    # Exceed max range
    with pytest.raises(InvalidTimeRangeError):
        service.get_summary(now - timedelta(days=35), now)
