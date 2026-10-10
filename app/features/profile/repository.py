"""
Users repository — database operations for user profile queries.
"""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.users import User

logger = get_logger(__name__)


def get_user_profile_by_id(db: Session, user_id: int) -> User | None:

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        logger.debug("DB query — get_user_profile_by_id: user_id=%s  email=%s", user.id, user.email)
    else:
        logger.debug("DB query — get_user_profile_by_id: user_id=%s not found", user_id)
    return user
