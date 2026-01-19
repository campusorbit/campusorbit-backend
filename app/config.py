from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/campusorbit"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "CampusOrbit ERP"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3001"

    # Institute
    INSTITUTE_NAME: str = "CampusOrbit Institute"
    INSTITUTE_CODE: str = "COI"

    # Razorpay
    RAZORPAY_PAYMENT_BUTTON_ID: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
