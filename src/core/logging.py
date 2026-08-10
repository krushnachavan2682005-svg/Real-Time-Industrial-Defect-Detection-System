import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO", name: Optional[str] = None
) -> logging.Logger:
    """
    Configures standard Python logging for the application.
    """
    logger = logging.getLogger(name or "industrial_defect_detection")

    # Prevent adding handlers multiple times if configured again
    if not logger.handlers:
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Do not propagate up to root logger to avoid duplicate logs in some frameworks
        logger.propagate = False

    return logger
