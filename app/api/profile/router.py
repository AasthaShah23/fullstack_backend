"""
Profile router — HTTP route handlers for user profile endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.logging import get_logger
from app.features.profile.schema import UserProfileResponse
from app.features.profile.service import get_current_user_profile
from app.models.users import User

logger = get_logger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Retrieves profile details of the currently authenticated user."
    ),
)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    return get_current_user_profile(db, current_user=current_user)

