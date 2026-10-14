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

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()