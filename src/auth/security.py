from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

from src.auth.config import auth_settings, security_config

# Configure Passlib to use bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = security_config.get("jwt", {}).get("algorithm", "HS256")


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire_minutes = security_config.get("jwt", {}).get(
            "access_token_expire_minutes", auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, auth_settings.JWT_SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(
            token, auth_settings.JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Could not validate credentials")
