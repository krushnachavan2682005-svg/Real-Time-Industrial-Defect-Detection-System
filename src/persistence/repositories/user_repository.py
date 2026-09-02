import logging
from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from src.persistence.exceptions import PersistenceError
from src.persistence.models import UserModel

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def create_user(self, username: str, password_hash: str, role: str) -> UserModel:
        try:
            with self.session_factory() as session:
                user = UserModel(
                    username=username, password_hash=password_hash, role=role
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise PersistenceError(f"Failed to create user: {e}") from e

    def get_by_username(self, username: str) -> Optional[UserModel]:
        try:
            with self.session_factory() as session:
                return (
                    session.query(UserModel)
                    .filter(UserModel.username == username)
                    .first()
                )
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            raise PersistenceError(f"Failed to get user: {e}") from e

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        try:
            with self.session_factory() as session:
                return session.query(UserModel).filter(UserModel.id == user_id).first()
        except Exception as e:
            logger.error(f"Failed to get user by id: {e}")
            raise PersistenceError(f"Failed to get user: {e}") from e

    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        try:
            with self.session_factory() as session:
                return session.query(UserModel).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise PersistenceError(f"Failed to list users: {e}") from e
