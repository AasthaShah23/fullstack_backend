from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.features.admin.repository import get_all_users
from app.features.admin.schema import UserListResponse
from app.features.auth.schema import UserResponse

logger = get_logger(__name__)


def list_users(db: Session, *, skip: int = 0, limit: int = 100) -> UserListResponse:
    users, total = get_all_users(db, skip=skip, limit=limit)
    logger.info("Admin user list retrieved: count=%d  total=%d", len(users), total)
    return UserListResponse(
        total=total,
        users=[UserResponse.model_validate(user) for user in users],
    )

