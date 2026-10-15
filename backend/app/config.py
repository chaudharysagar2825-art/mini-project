from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# C:\mini-project
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# C:\mini-project\.env
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    cors_allow_credentials: bool = False

    # Multi-channel integrations
    sms_provider: str = "mock"
    ivr_provider: str = "mock"
    sms_gateway_url: str | None = None
    sms_gateway_key: str | None = None
    sms_sender_id: str = "MANAS-SETU"
    ivr_webhook_secret: str | None = None


    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()