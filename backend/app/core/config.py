
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: ai-interview-coach/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

# Explicitly load environment variables from the project root.
load_dotenv(ENV_FILE, override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )

    database_url: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_model: str = "gpt-5.4-mini"
    llm_timeout_seconds: float = 60.0
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    @model_validator(mode="after")
    def _sync_postgres_password(self) -> "Settings":
        pg_password = os.getenv("POSTGRES_PASSWORD", "")
        if pg_password and ":change-me@" in self.database_url:
            self.database_url = self.database_url.replace(
                ":change-me@",
                f":{quote_plus(pg_password)}@",
                1,
            )
        return self


settings = Settings()
