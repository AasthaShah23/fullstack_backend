# TongGarden Backend API

A production-ready REST API built with **FastAPI**, **SQLAlchemy 2**, and **PostgreSQL** — structured for scalability, testability, and clean code.

---

## 🛠 Tech Stack

| Layer            | Technology                                  |
| :--------------- | :------------------------------------------ |
| Framework        | [FastAPI](https://fastapi.tiangolo.com/)    |
| Server           | [Uvicorn](https://www.uvicorn.org/)         |
| ORM              | [SQLAlchemy 2](https://www.sqlalchemy.org/) |
| Migrations       | [Alembic](https://alembic.sqlalchemy.org/)  |
| Database         | [PostgreSQL](https://www.postgresql.org/)   |
| DB Driver        | `psycopg2-binary`                           |
| Password Hashing | `argon2-cffi`                               |
| Validation       | [Pydantic v2](https://docs.pydantic.dev/)   |
| Config           | `python-dotenv`                             |

---

## 📁 Project Structure

```text
fullstack_backend/
│
├── alembic/                          # Database migration engine
│   ├── versions/                     # Auto-generated + manual migration files
│   │   ├── 958da1df6fcd_create_users_table.py
│   │   ├── 645261d1df41_seed_new_user_as_admin_role.py
│   │   ├── 36f3bc6327cc_create_refresh_token_table.py
│   │   └── e465d1c1f4de_create_password_resets_table.py
│   ├── env.py                        # Alembic runtime — wires SQLAlchemy models
│   └── script.py.mako                # Migration file template
│
├── app/
│   ├── api/                          # HTTP layer — routers only (thin controllers)
│   │   ├── __init__.py               # Aggregates all feature routers → api_router
│   │   └── auth/
│   │       ├── __init__.py
│   │       └── router.py             # Auth routes (signup, login, refresh, logout, password reset)
│   │
│   ├── core/                         # Shared infrastructure — no business logic here
│   │   ├── config.py                 # Settings loaded from .env (single source of truth)
│   │   ├── database.py               # SQLAlchemy engine, SessionLocal, Base
│   │   ├── deps.py                   # FastAPI dependencies (get_db session injector)
│   │   ├── logging.py                # setup_logging() + get_logger() factory
│   │   ├── security.py              # hash_password() / verify_password() — Argon2
│   │   └── security_middleware.py   # Role-based access control & rate limiting middleware
│   │
│   ├── features/                     # Feature-slice modules (co-locate by feature)
│   │   ├── admin/                    # Admin specific handlers & router
│   │   ├── auth/                     # Auth repository, schema, service
│   │   └── users/                    # User profile /me router
│   │
│   ├── models/                       # SQLAlchemy ORM table definitions
│   │   ├── __init__.py               # Exports User, RefreshToken, PasswordResetToken
│   │   ├── users.py                  # users table
│   │   ├── refresh_tokens.py         # refresh_tokens table
│   │   ├── password_resets.py        # password_resets table
│   │   └── seed_admin.py            # Standalone script to seed the admin user
│   │
│   └── main.py                       # App entry point — logging bootstrap, middleware, routers
│
├── .env                              # Your local secrets (git-ignored)
├── .env.example                      # Template — copy this to .env
├── .gitignore
├── alembic.ini                       # Alembic config (DB URL read from .env)
├── requirements.txt                  # Pinned dependencies
└── README.md
```

---

## 🗄️ Database Schema

### `users`

| Column              | Type           | Constraints                         | Description               |
| :------------------ | :------------- | :---------------------------------- | :------------------------ |
| `id`                | `Integer`      | PK, Indexed                         | Auto-increment identifier |
| `name`              | `String`       | `NOT NULL`                          | Full display name         |
| `email`             | `String`       | Unique, Indexed, `NOT NULL`         | Login email               |
| `password`          | `String`       | `NOT NULL`                          | Argon2 password hash      |
| `role`              | `String`       | `default='user'`, `NOT NULL`        | `admin` or `user`         |
| `is_email_verified` | `Boolean`      | `default=False`, `NOT NULL`         | Email verification flag   |
| `is_active`         | `Boolean`      | `default=True`, `NOT NULL`          | Account status flag       |
| `created_at`        | `DateTime(tz)` | `server_default=now()`              | Creation timestamp        |
| `updated_at`        | `DateTime(tz)` | `server_default=now()`, auto-update | Last modified timestamp   |

### `refresh_tokens`

| Column       | Type           | Constraints                         | Description                       |
| :----------- | :------------- | :---------------------------------- | :-------------------------------- |
| `id`         | `Integer`      | PK, Indexed                         | Auto-increment identifier         |
| `user_id`    | `Integer`      | FK → `users.id` CASCADE, `NOT NULL` | Owner reference                   |
| `token_hash` | `String`       | Unique, Indexed, `NOT NULL`         | Hashed refresh token              |
| `expires_at` | `DateTime(tz)` | `NOT NULL`                          | Token expiry                      |
| `revoked_at` | `DateTime(tz)` | Nullable                            | Null if active, set on revocation |
| `created_at` | `DateTime(tz)` | `server_default=now()`              | Issuance timestamp                |
| `updated_at` | `DateTime(tz)` | `server_default=now()`, auto-update | Last modified timestamp           |

### `password_resets`

| Column       | Type           | Constraints                         | Description                       |
| :----------- | :------------- | :---------------------------------- | :-------------------------------- |
| `id`         | `Integer`      | PK, Indexed                         | Auto-increment identifier         |
| `user_id`    | `Integer`      | FK → `users.id` CASCADE, `NOT NULL` | Owner reference                   |
| `token_hash` | `String`       | Unique, Indexed, `NOT NULL`         | Hashed reset token                |
| `expires_at` | `DateTime(tz)` | `NOT NULL`                          | 15-minute token expiry            |
| `used_at`    | `DateTime(tz)` | Nullable                            | Null until single-use consumption |
| `created_at` | `DateTime(tz)` | `server_default=now()`              | Request timestamp                 |

---

## 🚀 Local Setup

### Prerequisites

Make sure you have these installed before starting:

| Tool       | Version | Download                        |
| :--------- | :------ | :------------------------------ |
| Python     | 3.11+   | https://python.org/downloads    |
| PostgreSQL | 14+     | https://postgresql.org/download |
| Git        | any     | https://git-scm.com             |

---

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd fullstack_backend
```

---

### Step 2 — Create a local PostgreSQL database

Use **pgAdmin** — the official PostgreSQL GUI that comes bundled with every PostgreSQL installer (Windows, macOS, Linux). No terminal path issues, works the same everywhere.

> Don't have pgAdmin? Download it free from https://www.pgadmin.org/download/

**Follow these steps:**

**1.** Open **pgAdmin** and connect to your local server

- In the left panel expand **Servers → PostgreSQL**
- Enter your `postgres` user password if prompted

**2.** Right-click on **Databases** → click **Create → Database…**

**3.** In the **General** tab, set the **Database** name to:

```
fullstack_task
```

**4.** Click **Save**

**5.** You should now see `fullstack_task` listed under **Databases** in the left panel ✅

> **Note:** Make sure the PostgreSQL server service is running before opening pgAdmin.
>
> - **Windows** — Search _Services_ → find `postgresql-x64-16` → click **Start**
> - **macOS** — Run `brew services start postgresql@16` in Terminal
> - **Linux** — Run `sudo systemctl start postgresql` in Terminal

---

### Step 3 — Create and activate a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Configure environment variables

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Now open `.env` and fill in your database credentials:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fullstack_task
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

> **Replace** `your_password` with the password you set during PostgreSQL installation.  
> If you installed PostgreSQL with no password, use: `postgresql://postgres@localhost:5432/fullstack_task`

---

### Step 6 — Run database migrations

Apply all migrations (creates tables + seeds the admin user):

```bash
alembic upgrade head
```

Verify the migration ran successfully:

```bash
alembic current
```

You should see the latest revision ID (`36f3bc6327cc`) with `(head)` next to it.

---

### Step 7 — Start the development server

```bash
uvicorn app.main:app --reload
```

The server is now running at:

| URL                         | Description            |
| :-------------------------- | :--------------------- |
| http://localhost:8000       | Health check (`GET /`) |
| http://localhost:8000/docs  | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc API reference    |

---

## 🔑 Default Admin Account

The migration automatically seeds an admin user:

| Field     | Value              |
| :-------- | :----------------- |
| **Name**  | Aastha Shah        |
| **Email** | `aastha@gmail.com` |
| **Role**  | `admin`            |

> The seed is **idempotent** — running `alembic upgrade head` multiple times will not create duplicate rows.

---

## 📡 API Endpoints

### Auth Summary

| Method     | Endpoint                        | Description                                         | Auth   |
| :--------- | :------------------------------ | :-------------------------------------------------- | :----- |
| `POST`     | `/api/auth/signup`              | Register a new user account                         | Public |
| `POST`     | `/api/auth/login`               | Authenticate existing user (Rate limited 5/min)     | Public |
| `POST`     | `/api/auth/refresh`             | Obtain new access token & rotate refresh token      | Public |
| `POST`     | `/api/auth/logout`              | Revoke refresh token (`revoked_at = now()`)         | Public |
| `POST`     | `/api/auth/forgot-password`     | Request password reset link (Rate limited 3/min)    | Public |
| `POST`     | `/api/auth/reset-password`      | Reset password using token (Rate limited 5/min)     | Public |
| `GET/POST` | `/api/auth/verify-email`        | Verify email using 24h verification token           | Public |
| `POST`     | `/api/auth/resend-verification` | Resend email verification link (Rate limited 3/min) | Public |

### Profile Summary

| Method | Endpoint          | Description                   | Auth                               |
| :----- | :---------------- | :---------------------------- | :--------------------------------- |
| `GET`  | `/api/profile/me` | Get profile of logged-in user | `Bearer` (Requires verified email) |

### Admin Summary

| Method | Endpoint           | Description                           | Auth                    |
| :----- | :----------------- | :------------------------------------ | :---------------------- |
| `GET`  | `/api/admin/users` | List all registered users (paginated) | `Bearer` (`admin` role) |

---

### Endpoint Details

#### 1. `POST /api/auth/signup`

Registers a new user account with strong password validation (requires uppercase, lowercase, digit, and special character).

**Request Body:**

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "Str0ng!Pass123"
}
```

**Success — `201 Created`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a3f8c2d9e1...",
  "user": {
    "id": 5,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "user"
  }
}
```

**Errors:**

- `409 Conflict`: An account with this email address already exists.
- `422 Unprocessable Entity`: Password fails strength requirements or min length.

---

#### 2. `POST /api/auth/login`

Authenticates user credentials and issues new access and refresh tokens. Rate limited to **5 attempts per minute per IP** to prevent brute-force attacks.

**Request Body:**

```json
{
  "email": "jane@example.com",
  "password": "Str0ng!Pass123"
}
```

**Success — `200 OK`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "b9f2c1d8e4...",
  "user": {
    "id": 5,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "user"
  }
}
```

**Errors:**

- `401 Unauthorized`: Invalid email or password.
- `403 Forbidden`: Account is deactivated.
- `429 Too Many Requests`: Exceeded 5 login attempts per minute per IP.

---

#### 3. `POST /api/auth/refresh`

Exchanges an active refresh token for a new access token (15 mins) and a rotated refresh token (7 days).

**Request Body:**

```json
{
  "refresh_token": "b9f2c1d8e4..."
}
```

**Success — `200 OK`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "c7a1b3d5e9...",
  "user": {
    "id": 5,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "user"
  }
}
```

**Errors:**

- `401 Unauthorized`: Refresh token is invalid, expired, or revoked.

---

#### 4. `POST /api/auth/logout`

Revokes the refresh token in PostgreSQL by updating its `revoked_at` timestamp.

**Request Body:**

```json
{
  "refresh_token": "c7a1b3d5e9..."
}
```

**Success — `200 OK`:**

```json
{
  "message": "Successfully logged out."
}
```

**Errors:**

- `400 Bad Request`: Refresh token is invalid or already revoked.

---

#### 5. `GET /api/users/me`

Retrieves profile details of the currently authenticated user. **Protected route — accessible to any logged-in user regardless of role (`user` or `admin`).**

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Success — `200 OK`:**

```json
{
  "id": 5,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "is_email_verified": false,
  "is_active": true,
  "created_at": "2026-10-09T15:27:00Z"
}
```

**Errors:**

- `401 Unauthorized`: Missing, invalid, or expired JWT access token.
- `404 Not Found`: User profile not found.

---

#### 6. `GET /api/admin/users`

Lists all registered non-admin users (`role = 'user'`). **Strictly requires `admin` role.**

**Query Parameters:**

- `skip` _(int, optional, default: 0)_: Number of records to skip for pagination.
- `limit` _(int, optional, default: 100, max: 500)_: Max number of records to return.

**Headers:**

```http
Authorization: Bearer <admin_access_token>
```

**Success — `200 OK`:**

```json
{
  "total": 1,
  "users": [
    {
      "id": 2,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "role": "user"
    }
  ]
}
```

**Errors:**

- `401 Unauthorized`: Missing, invalid, or expired JWT access token.
- `403 Forbidden`: Authenticated user does not have the `admin` role.

---

#### 7. `POST /api/auth/forgot-password`

Generates a secure 15-minute single-use reset token and logs the mock password reset link to application logs. Always returns a generic success response to prevent user email enumeration. Rate limited to **3 attempts per minute per IP**.

**Request Body:**

```json
{
  "email": "jane@example.com"
}
```

**Success — `200 OK`:**

```json
{
  "message": "If the email is registered, password reset instructions have been sent."
}
```

**Errors:**

- `429 Too Many Requests`: Exceeded 3 requests per minute per IP.

---

#### 8. `POST /api/auth/reset-password`

Validates the 15-minute reset token, enforces password strength rules, updates user's password using Argon2 hashing, consumes the token (`used_at = now()`), and revokes all active refresh tokens for security. Rate limited to **5 attempts per minute per IP**.

**Request Body:**

```json
{
  "token": "4f9a2b8c...",
  "new_password": "N3w$ecurePass123"
}
```

**Success — `200 OK`:**

```json
{
  "message": "Password has been reset successfully. Please log in with your new password."
}
```

**Errors:**

- `400 Bad Request`: Token is invalid, expired, or already used.
- `422 Unprocessable Entity`: Password fails strength requirements (uppercase, lowercase, digit, special character, min 8 chars).
- `429 Too Many Requests`: Exceeded 5 requests per minute per IP.

---

#### 9. `GET /api/auth/verify-email?token=...` or `POST /api/auth/verify-email`

Validates the 24-hour verification token received from the mock email link (`http://localhost:3000/verify-email?token=...`), sets `user.is_email_verified = True`, and marks the token as used (`used_at = now()`).

**GET Query Parameter / POST Request Body:**

`token`: Raw token string.

**Success — `200 OK`:**

```json
{
  "message": "Email has been successfully verified. You can now access all features."
}
```

**Errors:**

- `400 Bad Request`: Token is invalid, expired, or already used.

---

#### 10. `POST /api/auth/resend-verification`

Generates a fresh 24-hour verification token and logs a new mock verification link for unverified users. Rate limited to **3 attempts per minute per IP**.

**Request Body:**

```json
{
  "email": "jane@example.com"
}
```

**Success — `200 OK`:**

```json
{
  "message": "If the email is registered and unverified, a new verification link has been sent."
}
```

**Errors:**

- `429 Too Many Requests`: Exceeded 3 requests per minute per IP.

---

## 🛠 Common Development Commands

| Action                     | Command                                                |
| :------------------------- | :----------------------------------------------------- |
| Start server (with reload) | `uvicorn app.main:app --reload`                        |
| Apply all migrations       | `alembic upgrade head`                                 |
| Roll back last migration   | `alembic downgrade -1`                                 |
| Check current migration    | `alembic current`                                      |
| View migration history     | `alembic history --verbose`                            |
| Create a new migration     | `alembic revision --autogenerate -m "describe change"` |
| Seed admin user manually   | `python -m app.models.seed_admin`                      |
| Run Linter (Ruff)          | `ruff check --fix .`                                   |
| Format Codebase (Ruff)     | `ruff format .`                                        |

---

## 🧹 Code Formatting & Linting (Ruff)

This project uses **[Ruff](https://docs.astral.sh/ruff/)** for fast Python linting and code formatting.

### 1. Installation

Ruff is included in `requirements.txt` and is installed automatically when setting up the environment:

```bash
pip install -r requirements.txt
```

### 2. Formatting Code

To auto-format all Python files in the project to comply with PEP 8 and project style guidelines:

```bash
ruff format .
```

### 3. Running the Linter

To check for code errors, unused imports, or style violations and automatically fix them:

```bash
ruff check --fix .
```

---

## 🪵 Logging

Logs are written to **stdout** in this format:

```
2026-10-08 12:00:00 | INFO     | app.api.auth.router | signup:31 | Signup request received for email=jane@example.com
2026-10-08 12:00:00 | DEBUG    | app.features.auth.service | signup_user:40 | Checking email availability
2026-10-08 12:00:00 | INFO     | app.main | log_requests:45 | RESPONSE [a1b2c3d4] status=201  duration=42.15ms
```

Control verbosity via `.env`:

```env
LOG_LEVEL=DEBUG    # Show everything (development)
LOG_LEVEL=INFO     # Show business events only (staging)
LOG_LEVEL=WARNING  # Show warnings and errors only (production)
```

---

## ⚙️ Architecture Overview

```
Request
  │
  ▼
app/api/auth/router.py       ← HTTP layer    (FastAPI route, request/response models)
  │
  ▼
app/features/auth/service.py ← Business layer (validation logic, error handling)
  │
  ▼
app/features/auth/repository.py ← Data layer (all SQL/ORM queries, DB session)
  │
  ▼
PostgreSQL
```

Each layer has a **single responsibility** — this makes the code easy to test, maintain, and extend.
