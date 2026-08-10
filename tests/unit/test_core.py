import pytest


def test_config_initialization():
    from src.core.config import Settings, settings

    assert settings is not None
    assert isinstance(settings, Settings)
    assert hasattr(settings, "APP_ENV")


def test_constants_accessible():
    from src.core.constants import APP_NAME

    assert APP_NAME == "Real-Time Industrial Defect Detection System"


def test_exception_hierarchy():
    from src.core.exceptions import ApplicationError, ConfigurationError

    with pytest.raises(ApplicationError):
        raise ConfigurationError("Test error")


def test_logging_initialization():
    import logging

    from src.core.logging import configure_logging

    logger = configure_logging(level="DEBUG", name="test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG
    assert logger.name == "test_logger"
