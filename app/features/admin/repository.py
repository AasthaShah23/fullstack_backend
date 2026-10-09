from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.users import User

logger = get_logger(__name__)


def get_all_users(db: Session, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    base_query = db.query(User).filter(User.role == "user")
    total = base_query.count()
    users = base_query.order_by(User.id.asc()).offset(skip).limit(limit).all()
    return users, total

