from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.logging import get_logger
from app.schemas.auth import SignUpRequest, SignUpResponse, UserResponse
from app.services.auth_service import signup_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user with the `user` role. "
        "Returns the created user's public profile. "
        "Fails with **409 Conflict** if the email is already registered."
    ),
)
def signup(
    payload: SignUpRequest,
    db: Session = Depends(get_db),
) -> SignUpResponse:
    user = signup_user(db, payload)

    logger.info(
        "Signup successful — user_id=%s  email=%s  role=%s",
        user.id,
        user.email,
        user.role,
    )

    return SignUpResponse(
        message="Account created successfully.",
        user=UserResponse.model_validate(user),
    )
