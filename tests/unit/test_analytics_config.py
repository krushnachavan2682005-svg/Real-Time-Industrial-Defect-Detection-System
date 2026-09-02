import pytest
import yaml
from src.analytics.config import load_analytics_config, AnalyticsSettings
from src.core.exceptions import ConfigurationError

def test_load_analytics_config_default(tmp_path):
    # Missing file should return defaults
    cfg = load_analytics_config(str(tmp_path / "missing.yaml"))
    assert cfg.default_page_size == 100
    assert cfg.max_time_range_days == 365

def test_load_analytics_config_valid(tmp_path):
    cfg_file = tmp_path / "analytics.yaml"
    data = {
        "analytics": {
            "default_page_size": 50,
            "thresholds": {
                "high_reject_rate": 0.2
            }
        }
    }
    with open(cfg_file, "w") as f:
        yaml.dump(data, f)
        
    cfg = load_analytics_config(str(cfg_file))
    assert cfg.default_page_size == 50
    assert cfg.thresholds.high_reject_rate == 0.2
