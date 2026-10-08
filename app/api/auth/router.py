from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.logging import get_logger
from app.features.auth.schema import LoginRequest, SignUpRequest, TokenResponse
from app.features.auth.service import login_user, signup_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

# POST /api/auth/signup
@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user with the `user` role. "
        "Returns a JWT **access token** (15 min) and an opaque **refresh token** (7 days). "
        "Fails with **409 Conflict** if the email is already registered."
    ),
)
def signup(
    payload: SignUpRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    logger.info("Signup request received for email=%s", payload.email)
    token_response = signup_user(db, payload)
    logger.info(
        "Signup complete — user_id=%s  email=%s",
        token_response.user.id,
        token_response.user.email,
    )
    return token_response

# POST /api/auth/login
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description=(
        "Authenticates an existing user."
    ),
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    token_response = login_user(db, payload)
    return token_response