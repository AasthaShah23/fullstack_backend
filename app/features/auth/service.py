from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.features.auth.repository import (
    create_refresh_token,
    create_user,
    get_hash_refresh_token,
    get_user_by_email,
    get_user_by_id,
    revoke_refresh_token,
)
from app.features.auth.schema import (
    LoginRequest,
    RefreshTokenRequest,
    SignUpRequest,
    TokenResponse,
    UserResponse,
)

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


def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = get_user_by_email(db, email=payload.email)

    if not user or not verify_password(payload.password, user.password):
        logger.warning(
            "Login failed — invalid credentials for email=%s", payload.email
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        logger.warning(
            "Login rejected — account deactivated for user_id=%s  email=%s",
            user.id,
            user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    # Generate JWT access token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    # Generate + store refresh token
    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)
    create_refresh_token(db, user_id=user.id, token_hash=token_hash)

    logger.info(
        "Login successful — user_id=%s  email=%s  role=%s",
        user.id,
        user.email,
        user.role,
    )

    # Return response
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        user=UserResponse.model_validate(user),
    )


def refresh_access_token(db: Session, payload: RefreshTokenRequest) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access token and a new rotated refresh token.

    Steps:
        1. Hash the incoming raw refresh token.
        2. Query database for matching token record.
        3. Validate record exists, is not revoked, and is not expired.
        4. Validate user exists and is active.
        5. Revoke old refresh token (Token Rotation).
        6. Generate and store a new refresh token.
        7. Generate a new JWT access token.
        8. Return new tokens + user profile.
    """
    token_hash = hash_refresh_token(payload.refresh_token)
    token_record = get_hash_refresh_token(db, token_hash)

    if not token_record:
        logger.warning("Refresh failed — token hash not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    if token_record.revoked_at is not None:
        logger.warning(
            "Refresh failed — token id=%s was already revoked at %s",
            token_record.id,
            token_record.revoked_at,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    now = datetime.now(timezone.utc)
    expires_at = token_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        logger.warning("Refresh failed — token id=%s has expired", token_record.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user = get_user_by_id(db, token_record.user_id)
    if not user or not user.is_active:
        logger.warning(
            "Refresh failed — user_id=%s does not exist or is inactive",
            token_record.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or no longer exists.",
        )

    # Token Rotation: Revoke old token, create new token
    revoke_refresh_token(db, token_record)

    new_raw_refresh_token = generate_refresh_token()
    new_token_hash = hash_refresh_token(new_raw_refresh_token)
    create_refresh_token(db, user_id=user.id, token_hash=new_token_hash)

    new_access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    logger.info(
        "Token refresh successful — user_id=%s  email=%s", user.id, user.email
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_raw_refresh_token,
        user=UserResponse.model_validate(user),
    )
