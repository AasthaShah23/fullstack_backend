from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
)
from app.features.auth.repository import (
    create_refresh_token,
    create_user,
    get_user_by_email,
)
from app.features.auth.schema import SignUpRequest, TokenResponse, UserResponse

logger = get_logger(__name__)

def signup_user(db: Session, payload: SignUpRequest) -> TokenResponse:
    """
    Register a new user account and return JWT tokens.

    Steps:
        1. Check the email is not already taken  → 409 if duplicate.
        2. Hash the plain-text password with Argon2.
        3. Persist the new user row.
        4. Generate a signed JWT access token (15 min).
        5. Generate a secure random refresh token (7 days).
        6. Store the SHA-256 hash of the refresh token in the DB.
        7. Return both tokens + public user profile.
    """
    # Duplicate email check
    existing_user = get_user_by_email(db, email=payload.email)
    if existing_user:
        logger.warning(
            "Email already registered: email=%s", payload.email
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

    # Generate JWT access token
    access_token = create_access_token(
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role,
    )

    # Generate + store refresh token
    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)

    create_refresh_token(db, user_id=new_user.id, token_hash=token_hash)
    logger.info(
        "Tokens issued after signup — user_id=%s", new_user.id
    )

    # Return response
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,   # raw token → goes to client
        user=UserResponse.model_validate(new_user),
    )
