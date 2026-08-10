class ApplicationError(Exception):
    """Base class for all application-specific exceptions."""

    pass


class ConfigurationError(ApplicationError):
    """Raised when there is an issue with the configuration (e.g., missing env vars)."""

    pass


class DataError(ApplicationError):
    """Raised when there is an issue with the data (e.g., missing files, corruption)."""

    pass


class ModelError(ApplicationError):
    """Raised when there is an issue with loading or handling the model."""

    pass


class InferenceError(ApplicationError):
    """Raised when an error occurs during inference (e.g., OpenCV failure,
    ONNX error)."""

    pass


class IntegrationError(ApplicationError):
    """Raised when communication with an external system (e.g., PLC) fails."""

    pass
