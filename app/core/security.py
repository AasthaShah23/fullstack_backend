import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_ph = PasswordHasher()

# Password hashing
def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using Argon2 and return the hash string."""
    return _ph.hash(plain_password)

# Password verify
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored Argon2 hash."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

# JWT — Access Token
def create_access_token(user_id: int, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(
        "Access token created — user_id=%s  expires_at=%s", user_id, expire.isoformat()
    )
    return token

# JWT — Decode Access Token
def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload

# Refresh Token — random opaque string stored as a hash in the DB
def generate_refresh_token() -> str:
    return secrets.token_hex(32) 

# Refresh Token — hash for DB storage
def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()

# Password Reset Token — random opaque string
def generate_reset_token() -> str:
    return secrets.token_hex(32)

# Password Reset Token — hash for DB storage
def hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()
