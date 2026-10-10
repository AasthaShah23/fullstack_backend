import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
    )
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

settings = Settings()

