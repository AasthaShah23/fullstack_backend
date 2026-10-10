from app.core.database import SessionLocal
from app.models.users import User

ADMIN_USER_DATA = {
    "name": "Aastha Shah",
    "email": "aastha@gmail.com",
    "password": "$argon2i$v=19$m=16,t=2,p=1$ckh6VzFqWldVN1Bqa1FBYg$4w03TMy0+1hKZGd5RuD0BA",
    "role": "admin",
    "is_email_verified": True,
    "is_active": True,
}


def seed_users():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == ADMIN_USER_DATA["email"]).first()
        if user:
            print(
                f"User with email '{ADMIN_USER_DATA['email']}' already exists. Updating details..."
            )
            for key, value in ADMIN_USER_DATA.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
            print(f"User '{user.email}' updated successfully (ID: {user.id}).")
        else:
            user = User(**ADMIN_USER_DATA)
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Admin user '{user.email}' seeded successfully (ID: {user.id}).")
        return user
    except Exception as e:
        db.rollback()
        print(f"Error seeding user: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
