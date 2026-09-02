import pytest
from src.analytics.aggregations import calculate_rates, generate_quality_alerts
from src.analytics.models import InspectionStatistics
from src.analytics.config import AnalyticsSettings

def test_calculate_rates():
    pr, revr, rejr = calculate_rates(70, 20, 10)
    assert pr == 0.7
    assert revr == 0.2
    assert rejr == 0.1

def test_calculate_rates_zero():
    pr, revr, rejr = calculate_rates(0, 0, 0)
    assert pr == 0.0
    assert revr == 0.0
    assert rejr == 0.0

def test_generate_quality_alerts():
    stats = InspectionStatistics(
        total_inspections=100,
        pass_count=70,
        review_count=15,
        reject_count=15,
        pass_rate=0.7,
        review_rate=0.15,
        reject_rate=0.15,
        average_defects_per_inspection=1.5,
        average_latency_ms=25.0
    )
    
    config = AnalyticsSettings()
    config.thresholds.high_reject_rate = 0.10
    config.thresholds.high_review_rate = 0.20
    
    alerts = generate_quality_alerts(stats, config)
    assert len(alerts) == 1
    assert alerts[0].severity == "HIGH"
    assert alerts[0].metric == "reject_rate"
    
    config.thresholds.high_review_rate = 0.10
    alerts = generate_quality_alerts(stats, config)
    assert len(alerts) == 2
