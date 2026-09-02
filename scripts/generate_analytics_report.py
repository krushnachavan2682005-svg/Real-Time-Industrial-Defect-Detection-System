import os
import sys
import yaml
import json
import argparse
from datetime import datetime

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.persistence.database import db
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository
from src.analytics.config import load_analytics_config
from src.analytics.service import AnalyticsService

def generate_report(start_time: str = None, end_time: str = None, interval: str = "day"):
    # Load persistence config directly
    db_config_path = "configs/persistence/database.yaml"
    try:
        with open(db_config_path, "r") as f:
            db_config = yaml.safe_load(f)
    except Exception as e:
        print(f"Failed to load db config: {e}")
        return

    # Initialize DB
    db_url = db_config.get("database", {}).get("url", "sqlite:///data/industrial_defect.db")
    db.initialize(db_url)
    repo = SQLAlchemyInspectionRepository(db.get_session)
    
    # Load analytics config
    analytics_config = load_analytics_config()
    service = AnalyticsService(repo, analytics_config)
    
    # Parse time args if present
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None
    
    try:
        summary = service.get_summary(start_dt, end_dt)
    except Exception as e:
        print(f"Failed to generate summary: {e}")
        return

    # Ensure output dir exists
    os.makedirs("reports/analytics", exist_ok=True)
    report_path = "reports/analytics/analytics_report.json"
    
    with open(report_path, "w") as f:
        # Pydantic model dump
        json.dump(summary.model_dump(mode='json'), f, indent=2)
        
    print(f"Analytics report successfully generated at {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Industrial Defect Analytics Report")
    parser.add_argument("--start-time", type=str, help="Start time in ISO format")
    parser.add_argument("--end-time", type=str, help="End time in ISO format")
    parser.add_argument("--interval", type=str, default="day", help="Trend interval")
    
    args = parser.parse_args()
    generate_report(args.start_time, args.end_time, args.interval)
