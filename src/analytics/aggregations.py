from typing import List
from src.analytics.models import InspectionStatistics, QualityAlert
from src.analytics.config import AnalyticsSettings

def calculate_rates(pass_count: int, review_count: int, reject_count: int) -> tuple[float, float, float]:
    total = pass_count + review_count + reject_count
    if total == 0:
        return 0.0, 0.0, 0.0
    return (
        pass_count / total,
        review_count / total,
        reject_count / total
    )

def generate_quality_alerts(stats: InspectionStatistics, config: AnalyticsSettings) -> List[QualityAlert]:
    alerts = []
    
    if stats.reject_rate > config.thresholds.high_reject_rate:
        alerts.append(QualityAlert(
            severity="HIGH",
            message="Reject rate exceeds configured production threshold.",
            metric="reject_rate",
            threshold=config.thresholds.high_reject_rate,
            actual_value=stats.reject_rate
        ))
        
    if stats.review_rate > config.thresholds.high_review_rate:
        alerts.append(QualityAlert(
            severity="MEDIUM",
            message="Review rate exceeds configured production threshold.",
            metric="review_rate",
            threshold=config.thresholds.high_review_rate,
            actual_value=stats.review_rate
        ))
        
    return alerts
