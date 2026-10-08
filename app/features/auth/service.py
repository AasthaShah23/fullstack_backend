"""
Auth service — business logic layer for authentication flows.

This layer sits between the route handlers (HTTP concerns) and the
repository layer (database concerns). It contains no framework-specific
code so it is easy to unit-test in isolation.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.users import User
from app.features.auth.schema import SignUpRequest
from app.features.auth.repository import get_user_by_email, create_user

logger = get_logger(__name__)


def signup_user(db: Session, payload: SignUpRequest) -> User:
    """
    Register a new user account.

    Steps:
        1. Check that the email address is not already taken.
        2. Hash the plain-text password with Argon2.
        3. Persist the new user via the repository layer.

    Args:
        db: Active SQLAlchemy session (injected by FastAPI).
        payload: Validated sign-up data from the request body.

    Returns:
        The newly created User ORM object.

    Raises:
        HTTPException 409: If the email address is already registered.
    """
    existing_user = get_user_by_email(db, email=payload.email)

    if existing_user:
        logger.warning(
            "Signup rejected — email already registered: email=%s", payload.email
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    hashed_pw = hash_password(payload.password)

    logger.debug("Creating user record for email=%s  name=%s", payload.email, payload.name)
    new_user = create_user(
        db,
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_pw,
    )

    logger.info(
        "User created successfully — user_id=%s  email=%s", new_user.id, new_user.email
    )
    return new_user
