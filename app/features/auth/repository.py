# User & RefreshToken repository — all database interactions live here.
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.password_resets import PasswordResetToken
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


def get_hash_refresh_token(db: Session, token_hash: str) -> RefreshToken | None:
    """Return the RefreshToken row matching *token_hash*, or None if not found."""
    token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if token:
        logger.debug("Found refresh token record: id=%s  user_id=%s", token.id, token.user_id)
    else:
        logger.debug("No refresh token record found for token_hash")
    return token


def revoke_refresh_token(db: Session, refresh_token: RefreshToken) -> None:
    """Mark a refresh token record as revoked by setting revoked_at to current timestamp."""
    try:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(refresh_token)
        logger.debug("Revoked refresh token id=%s for user_id=%s", refresh_token.id, refresh_token.user_id)
    except Exception:
        db.rollback()
        logger.error(
            "Failed to revoke refresh token id=%s", refresh_token.id, exc_info=True
        )
        raise


# Password Reset queries
def create_password_reset_token(
    db: Session,
    *,
    user_id: int,
    token_hash: str,
    expires_in_minutes: int = 15,
) -> PasswordResetToken:
    """Insert a new PasswordResetToken row into DB."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    reset_token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    try:
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)
        logger.debug(
            "Password reset token stored — user_id=%s  expires_at=%s",
            user_id,
            expires_at.isoformat(),
        )
    except Exception:
        db.rollback()
        logger.error(
            "Failed to store password reset token for user_id=%s", user_id, exc_info=True
        )
        raise
    return reset_token


def get_password_reset_token_by_hash(db: Session, token_hash: str) -> PasswordResetToken | None:
    """Return the PasswordResetToken row matching *token_hash*, or None if not found."""
    token = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    if token:
        logger.debug("Found password reset token: id=%s  user_id=%s", token.id, token.user_id)
    else:
        logger.debug("No password reset token found for hash")
    return token


def mark_password_reset_token_used(db: Session, reset_token: PasswordResetToken) -> None:
    """Mark a password reset token as used."""
    try:
        reset_token.used_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reset_token)
        logger.debug("Marked password reset token id=%s as used", reset_token.id)
    except Exception:
        db.rollback()
        logger.error(
            "Failed to mark password reset token id=%s as used", reset_token.id, exc_info=True
        )
        raise


def update_user_password(db: Session, user: User, new_hashed_password: str) -> None:
    """Update user password with new Argon2 hash."""
    try:
        user.password = new_hashed_password
        db.commit()
        db.refresh(user)
        logger.debug("Updated password for user_id=%s", user.id)
    except Exception:
        db.rollback()
        logger.error(
            "Failed to update password for user_id=%s", user.id, exc_info=True
        )
        raise


def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> None:
    """Revoke all active refresh tokens for a user (e.g. after password reset)."""
    try:
        now = datetime.now(timezone.utc)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now})
        db.commit()
        logger.debug("Revoked all active refresh tokens for user_id=%s", user_id)
    except Exception:
        db.rollback()
        logger.error(
            "Failed to revoke all refresh tokens for user_id=%s", user_id, exc_info=True
        )
        raise
