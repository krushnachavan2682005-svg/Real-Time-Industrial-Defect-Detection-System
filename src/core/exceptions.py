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


class DecisionError(ApplicationError):
    """Raised when an error occurs during decision logic evaluation."""

    pass


class DecisionConfigurationError(ConfigurationError):
    """Raised when there is an error in the decision rules configuration."""

    pass


class MappingError(ApplicationError):
    """Raised when an error occurs during defect mapping or spatial geometry calculations."""

    pass
