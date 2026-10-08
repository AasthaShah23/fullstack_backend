# User & RefreshToken repository — all database interactions live here.
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.refresh_tokens import RefreshToken
from app.models.users import User

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# User queries
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> User | None:
    """Return the User row matching *email*, or None if not found."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.debug("Found user: user_id=%s  email=%s", user.id, email)
    else:
        logger.debug("No user found for email=%s", email)
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return the User row matching *user_id*, or None if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        logger.debug("Found user: user_id=%s  email=%s", user.id, user.email)
    else:
        logger.debug("No user found for user_id=%s", user_id)
    return user


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    role: str = "user",
) -> User:
    """Insert a new user row and return the persisted instance."""
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        logger.error(
            "DB commit failed for email=%s — rolling back transaction",
            email,
            exc_info=True,
        )
        raise
    return user

# Refresh token queries
def create_refresh_token(db: Session, *, user_id: int, token_hash: str) -> RefreshToken:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    try:
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
    except Exception:
        db.rollback()
        logger.error(
            "Failed to store refresh token for user_id=%s", user_id, exc_info=True
        )
        raise
    return refresh_token
