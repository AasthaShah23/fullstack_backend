from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.logging import get_logger
from app.features.auth.schema import SignUpRequest, TokenResponse
from app.features.auth.service import signup_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

# Sign Up Route
@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user with the `user` role."
    ),
)
def signup(
    payload: SignUpRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    token_response = signup_user(db, payload)
    return token_response