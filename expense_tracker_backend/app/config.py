import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Configuration settings loaded from environment variables."""
    # Database connection (provided by dependent database container)
    DB_URL: str = os.getenv("DB_URL", "")
    # JWT secret and expiry
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ACCESS_TOKEN_EXPIRES_MIN: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MIN", "60"))
    # CORS origins (comma-separated)
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # App metadata
    API_TITLE: str = os.getenv("API_TITLE", "Expense Tracker API")
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    OPENAPI_URL_PREFIX: str = os.getenv("OPENAPI_URL_PREFIX", "/docs")
    OPENAPI_SWAGGER_UI_URL: str = os.getenv(
        "OPENAPI_SWAGGER_UI_URL", "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    def validate(self) -> None:
        """Validate critical configuration fields."""
        missing = []
        if not self.DB_URL:
            missing.append("DB_URL")
        if not self.JWT_SECRET_KEY:
            missing.append("JWT_SECRET_KEY")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


settings = Settings()
