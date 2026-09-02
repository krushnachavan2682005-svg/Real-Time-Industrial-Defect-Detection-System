from src.core.exceptions import ApplicationError

class PersistenceError(ApplicationError):
    """Base class for all persistence-related exceptions."""
    pass

class DatabaseConnectionError(PersistenceError):
    """Raised when there is an error connecting to the database."""
    pass

class InspectionPersistenceError(PersistenceError):
    """Raised when an error occurs while saving an inspection."""
    pass

class InspectionNotFoundError(PersistenceError):
    """Raised when an inspection is not found in the database."""
    pass
