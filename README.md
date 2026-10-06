# Backend API - FastAPI & PostgreSQL

A robust backend service built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, with database migrations managed by **Alembic**.

---

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Driver**: `psycopg2-binary`
- **Environment Management**: `python-dotenv`

---

## 📁 Project Structure

```text
backend/
├── alembic/                      # Alembic migration scripts and configuration
│   ├── versions/                 # Database migration revision files
│   └── env.py                    # Alembic runtime environment
├── app/
│   ├── core/
│   │   └── database.py           # Database engine, SessionLocal, and declarative Base
│   ├── models/
│   │   ├── __init__.py           # Model exports
│   │   ├── users.py              # User SQLAlchemy model schema
│   │   ├── refresh_tokens.py     # RefreshToken SQLAlchemy model schema
│   │   └── seed_admin.py         # Admin user database seeder script
│   └── main.py                   # FastAPI application initialization & routes
├── .env.example                  # Template for required environment variables
├── .gitignore                    # Git ignore file (excludes .venv and .env)
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Project dependencies
└── README.md                     # Setup and usage guide
```

---

## 📋 Database Schema

### `users` Table

| Column | Type | Constraints / Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Indexed | Unique user identifier |
| `name` | `String` | `nullable=False` | Full name of the user |
| `email` | `String` | Unique, Indexed, `nullable=False` | User email address |
| `password` | `String` | `nullable=False` | Hashed password string |
| `role` | `String` | `default="user"`, `nullable=False` | Role designation (`admin`, `user`, etc.) |
| `is_email_verified` | `Boolean` | `default=False`, `nullable=False` | Verification status flag |
| `is_active` | `Boolean` | `default=True`, `nullable=False` | Active status flag |
| `created_at` | `DateTime(timezone=True)` | `server_default=now()`, `nullable=False` | Record creation timestamp |
| `updated_at` | `DateTime(timezone=True)` | `server_default=now()`, auto-updates | Record modification timestamp |

### `refresh_tokens` Table

| Column | Type | Constraints / Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Indexed | Unique token identifier |
| `user_id` | `Integer` | Foreign Key (`users.id`, `CASCADE`), Indexed, `nullable=False` | Associated user reference |
| `token_hash` | `String` | Unique, Indexed, `nullable=False` | Secure hash of the refresh token |
| `expires_at` | `DateTime(timezone=True)` | `nullable=False` | Expiration date and time |
| `revoked_at` | `DateTime(timezone=True)` | `nullable=True` | Revocation timestamp (null if active) |
| `created_at` | `DateTime(timezone=True)` | `server_default=now()`, `nullable=False` | Token issuance timestamp |
| `updated_at` | `DateTime(timezone=True)` | `server_default=now()`, auto-updates | Record update timestamp |

---

## 🚀 Getting Started (Local Setup)

### 1. Prerequisites

Ensure you have the following installed on your machine:
- **Python**: Version 3.11 or higher
- **PostgreSQL**: Installed and running locally
- **Git**

---

### 2. Navigate to Backend Directory

```bash
cd backend
```

---

### 3. Create and Activate Virtual Environment

Create an isolated Python environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate on macOS / Linux:
source .venv/bin/activate

# Or on Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

---

### 4. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 5. Configure Environment Variables

1. Copy the sample environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your PostgreSQL database connection URL:
   ```env
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
   SALT=your_salt_value_here
   ```

> **Note**: Make sure the PostgreSQL database specified in `DATABASE_URL` exists before running migrations. You can create it using `createdb <database_name>` or via PostgreSQL CLI / pgAdmin.

---

### 6. Run Database Migrations

Apply existing Alembic migrations to create all database tables and indexes:

```bash
alembic upgrade head
```

To verify the current migration state:

```bash
alembic current
```

---

### 7. Seed the Initial Admin User

Run the idempotent admin seeding script to create or update the default admin user:

```bash
python -m app.models.seed_admin
```

#### Default Admin Credentials:
- **Name**: `Aastha Shah`
- **Email**: `aastha@gmail.com`
- **Role**: `admin`
- **Email Verified**: `True`
- **Active**: `True`

*(Note: The script is idempotent; if the email already exists, it updates the record instead of throwing a unique constraint error).*

---

### 8. Run the Development Server

Start the FastAPI application using Uvicorn with auto-reload enabled:

```bash
uvicorn app.main:app --reload
```

The application will start at:
- **API URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛠 Common Development Commands

| Action | Command |
| :--- | :--- |
| **Start server** | `uvicorn app.main:app --reload` |
| **Apply migrations** | `alembic upgrade head` |
| **Check migration status** | `alembic current` |
| **Create new migration** | `alembic revision --autogenerate -m "description"` |
| **Rollback migration** | `alembic downgrade -1` |
| **Seed admin user** | `python -m app.models.seed_admin` |
