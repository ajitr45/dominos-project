from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import (JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS, JWT_ALGORITHM, JWT_SECRET_KEY)


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    # Set token expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    # Store only the minimum identity information in the JWT
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token


def decode_access_token(token: str) -> dict:
    # Verify JWT signature and expiration
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    return payload

def create_refresh_token(user_id: int) -> str:
    # Set refresh token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        days=JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Store minimum identity information in the refresh token
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "refresh",
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token


def decode_refresh_token(token: str) -> dict:
    # Verify JWT signature and expiration
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    return payload