"""
Users service — business logic layer for user profile management.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.features.profile.repository import get_user_profile_by_id
from app.features.profile.schema import UserProfileResponse
from app.models.users import User

logger = get_logger(__name__)


def get_current_user_profile(db: Session, current_user: User) -> UserProfileResponse:
    user = get_user_profile_by_id(db, user_id=current_user.id)
    if not user:
        logger.warning("Profile lookup failed — user_id=%s not found", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    logger.info("User profile retrieved successfully — user_id=%s  email=%s", user.id, user.email)
    return UserProfileResponse.model_validate(user)

