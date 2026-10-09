from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.users import User

logger = get_logger(__name__)


def get_all_users(db: Session, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()
    logger.debug(
        "DB query — get_all_users: count=%d  total=%d  skip=%d  limit=%d",
        len(users),
        total,
        skip,
        limit,
    )
    return users, total

