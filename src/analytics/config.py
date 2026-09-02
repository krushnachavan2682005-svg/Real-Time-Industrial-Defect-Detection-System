from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
import yaml
from typing import Optional
from src.core.exceptions import ConfigurationError

class TrendConfig(BaseModel):
    default_interval: str = "day"

class ThresholdsConfig(BaseModel):
    high_reject_rate: float = 0.15
    high_review_rate: float = 0.10

class ReportingConfig(BaseModel):
    enabled: bool = True

class AnalyticsSettings(BaseSettings):
    default_page_size: int = 100
    max_time_range_days: int = 365
    trend: TrendConfig = Field(default_factory=TrendConfig)
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)

def load_analytics_config(config_path: str = "configs/analytics/analytics.yaml") -> AnalyticsSettings:
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            if not data or "analytics" not in data:
                return AnalyticsSettings()
            return AnalyticsSettings(**data["analytics"])
    except FileNotFoundError:
        return AnalyticsSettings()
    except Exception as e:
        raise ConfigurationError(f"Failed to load analytics config: {e}") from e

