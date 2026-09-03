import sys
from pathlib import Path
import uvicorn
import yaml
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.logging import configure_logging

logger = logging.getLogger(__name__)


def main():
    configure_logging()

    # Load API config just for server port/host
    try:
        with open("configs/api/api.yaml", "r") as f:
            api_config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load api.yaml: {e}")
        sys.exit(1)

    host = api_config.get("server", {}).get("host", "0.0.0.0")
    port = api_config.get("server", {}).get("port", 8000)

    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(
        "src.api.app:create_app", host=host, port=port, factory=True, reload=False
    )


if __name__ == "__main__":
    main()
