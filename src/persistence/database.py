import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.persistence.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def initialize(self, db_url: str, echo: bool = False, pool_enabled: bool = False, pool_size: int = 5, max_overflow: int = 10):
        try:
            connect_args = {}
            # For sqlite, we need check_same_thread=False if using multiple threads
            if db_url.startswith("sqlite"):
                connect_args["check_same_thread"] = False
            
            kwargs = {
                "echo": echo,
                "connect_args": connect_args
            }
            if pool_enabled and not db_url.startswith("sqlite"):
                kwargs["pool_size"] = pool_size
                kwargs["max_overflow"] = max_overflow
            
            self.engine = create_engine(db_url, **kwargs)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseConnectionError(f"Database connection failed: {e}") from e

    def get_session(self):
        if not self.SessionLocal:
            raise DatabaseConnectionError("Database has not been initialized.")
        return self.SessionLocal()

# Global database instance
db = Database()
