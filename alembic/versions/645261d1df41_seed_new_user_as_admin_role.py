"""seed new user as admin role

Revision ID: 645261d1df41
Revises: 958da1df6fcd
Create Date: 2026-10-06 17:04:43.193283

WHY THIS FILE WAS EMPTY:
    Alembic's --autogenerate only detects *schema* differences (tables, columns,
    indexes, constraints). Inserting a row is a *data* operation — Alembic has no
    knowledge of it, so it generated `pass`.  Data seeding must always be written
    by hand using op.execute() or the bulk_insert helper.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '645261d1df41'
down_revision: Union[str, Sequence[str], None] = '958da1df6fcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Seed data — keep in sync with app/models/seed_admin.py
# The password hash below is the Argon2 hash of the admin's initial password.
# ---------------------------------------------------------------------------
ADMIN_EMAIL = "aastha@gmail.com"
ADMIN_NAME = "Aastha Shah"
ADMIN_PASSWORD_HASH = (
    "$argon2i$v=19$m=16,t=2,p=1$ckh6VzFqWldVN1Bqa1FBYg$4w03TMy0+1hKZGd5RuD0BA"
)


def upgrade() -> None:
    """Insert the initial admin user row if it doesn't already exist."""

    # Use a helper table reference so we stay decoupled from the ORM model.
    # This prevents breakage if the User model changes in the future.
    users_table = sa.table(
        "users",
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("role", sa.String),
        sa.column("is_email_verified", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )

    # Guard: only insert if the row doesn't already exist (idempotent migration)
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    ).first()

    if result is None:
        op.bulk_insert(
            users_table,
            [
                {
                    "name": ADMIN_NAME,
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD_HASH,
                    "role": "admin",
                    "is_email_verified": True,
                    "is_active": True,
                }
            ],
        )


def downgrade() -> None:
    """Remove the seeded admin user row."""
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    )