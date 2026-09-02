import time

import pytest

from src.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "secure-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_token_generation():
    data = {"sub": "admin"}
    token = create_access_token(data=data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin"
    assert "exp" in decoded


def test_jwt_token_expiration():
    from datetime import timedelta

    data = {"sub": "admin"}
    # Token that expires in 1 second
    token = create_access_token(data=data, expires_delta=timedelta(seconds=1))
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin"

    # Wait for expiration
    time.sleep(2)
    with pytest.raises(ValueError, match="Token has expired"):
        decode_access_token(token)


def test_jwt_invalid_token():
    with pytest.raises(ValueError, match="Could not validate credentials"):
        decode_access_token("invalid.token.here")
