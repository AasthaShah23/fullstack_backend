# User repository — all database interactions for the User model live here.
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.users import User

logger = get_logger(__name__)

# Return the User row matching *email*, or None if not found.
def get_user_by_email(db: Session, email: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.debug("Found user: user_id=%s  email=%s", user.id, email)
    else:
        logger.debug("No user found for email=%s", email)
    return user

# Insert a new user row and return the persisted instance.
def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    role: str = "user",
) -> User:
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.debug(
            "DB commit successful — user_id=%s  email=%s", user.id, email
        )
    except Exception:
        db.rollback()
        logger.error(
            "DB commit failed for email=%s — rolling back transaction", email, exc_info=True
        )
        raise
    return user
