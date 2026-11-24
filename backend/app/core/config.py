
import os
from ipaddress import ip_network
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus, urlsplit, parse_qs

from dotenv import load_dotenv
from pydantic import Field, field_validator, model_validator
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
        hide_input_in_errors=True,
    )

    database_url: str = ""
    app_env: Literal["development", "test", "production"] = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=5, ge=0, le=20)
    db_pool_timeout: int = Field(default=10, ge=1, le=60)
    db_connect_timeout: int = Field(default=10, ge=1, le=60)
    staging_enabled: bool = False
    staging_access_mode: Literal["invite_only", "public"] = "invite_only"
    staging_allowed_emails: list[str] = []
    staging_registration_enabled: bool = False
    ai_enabled: bool = True
    speech_enabled: bool = True
    ai_global_concurrency: int = Field(default=8, ge=1, le=8)
    staging_ai_user_daily_limit: int = Field(default=30, ge=1, le=200)
    staging_ai_global_daily_limit: int = Field(default=100, ge=1, le=2000)
    forwarded_allow_ips: str = ""
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
    azure_speech_key: str = ""
    azure_speech_region: str = "eastasia"
    azure_speech_endpoint: str = ""

    @field_validator("staging_allowed_emails")
    @classmethod
    def _normalize_testers(cls, values: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(value.strip().lower() for value in values))
        if any(not value or value.count("@") != 1 or any(char.isspace() for char in value) for value in normalized):
            raise ValueError("STAGING_ALLOWED_EMAILS must contain exact tester emails.")
        return normalized

    @field_validator("forwarded_allow_ips")
    @classmethod
    def _validate_proxies(cls, value: str) -> str:
        for entry in filter(None, (part.strip() for part in value.split(","))):
            try:
                if ip_network(entry, strict=False).prefixlen == 0:
                    raise ValueError()
            except ValueError:
                raise ValueError("FORWARDED_ALLOW_IPS must contain explicit trusted IPs/CIDRs, never wildcard/all-address ranges.") from None
        return value

    @field_validator("cors_origins")
    @classmethod
    def _validate_origins(cls, values: list[str]) -> list[str]:
        if not values:
            raise ValueError("CORS_ORIGINS must contain explicit frontend origins.")
        for value in values:
            parsed = urlsplit(value)
            if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.path or "*" in value):
                raise ValueError("CORS_ORIGINS must contain exact HTTP(S) origins without paths or wildcards.")
            try:
                parsed.port
            except ValueError:
                raise ValueError("CORS_ORIGINS contains an invalid port.") from None
        return list(dict.fromkeys(values))

    @model_validator(mode="after")
    def _sync_postgres_password(self) -> "Settings":
        pg_password = os.getenv("POSTGRES_PASSWORD", "")
        if pg_password and ":change-me@" in self.database_url:
            self.database_url = self.database_url.replace(
                ":change-me@",
                f":{quote_plus(pg_password)}@",
                1,
            )
        if self.app_env == "production":
            if any(urlsplit(origin).scheme != "https" or urlsplit(origin).hostname in {"localhost", "127.0.0.1", "::1"} for origin in self.cors_origins):
                raise ValueError("Production CORS_ORIGINS must contain explicit public HTTPS origins.")
            database = urlsplit(self.database_url)
            if not database.scheme.startswith("postgresql") or parse_qs(database.query).get("sslmode", [""])[0] not in {"require", "verify-ca", "verify-full"}:
                raise ValueError("Production DATABASE_URL must use PostgreSQL with sslmode=require or certificate verification.")
        if self.staging_enabled:
            if self.app_env == "production" and parse_qs(urlsplit(self.database_url).query).get("sslmode", [""])[0] != "verify-full":
                raise ValueError("Restricted cloud staging requires sslmode=verify-full with a trusted database CA.")
            if self.staging_access_mode == "invite_only" and not self.staging_allowed_emails:
                raise ValueError("Restricted staging requires a nonempty STAGING_ALLOWED_EMAILS list.")
            if self.ai_global_concurrency > 2:
                raise ValueError("Restricted staging permits at most two concurrent AI endpoint requests.")
            if self.db_pool_size + self.db_max_overflow < self.ai_global_concurrency * 2 + 1:
                raise ValueError("Staging database pool must accommodate authentication and independent quota reservations.")
        return self


settings = Settings()
