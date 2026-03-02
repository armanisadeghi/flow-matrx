"""Centralized application configuration.

All settings are loaded once at startup from environment variables and/or the
.env file.  Import the singleton:

    from app.config import settings

Sub-groups keep related values together and readable:

    settings.primary_db.host
    settings.llm.openai_api_key.get_secret_value()
    settings.dirs.logs_dir
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import ClassVar

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class DatabaseSettings(BaseSettings):
    """Reusable for primary and secondary databases.

    Instantiated with an env_prefix so env vars stay flat:
        PRIMARY_DB_HOST, SECONDARY_DB_HOST, etc.
    """

    model_config = SettingsConfigDict(extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str = "postgres"
    user: str = "postgres"
    password: SecretStr = SecretStr("")
    protocol: str = "postgresql"

    # Supabase-specific connection fields
    project_url: str = ""
    publishable_key: SecretStr = SecretStr("")
    secret_key: SecretStr = SecretStr("")
    direct_connection_string: SecretStr = SecretStr("")

    @property
    def url(self) -> str:
        """Async-compatible connection URL (asyncpg)."""
        pw = self.password.get_secret_value()
        return f"{self.protocol}://{self.user}:{pw}@{self.host}:{self.port}/{self.name}"

class SupabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SUPABASE_", extra="ignore")

    url: str = ""
    jwt_secret: SecretStr = SecretStr("")
    publishable_key: SecretStr = SecretStr("")
    secret_key: SecretStr = SecretStr("")

    @property
    def configured(self) -> bool:
        return bool(self.url and self.jwt_secret.get_secret_value())


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    url: str = "redis://localhost:6379"


class LLMSettings(BaseSettings):
    """API keys for all supported LLM providers.

    All keys are optional — only configure the providers you use.
    """

    model_config = SettingsConfigDict(extra="ignore")

    openai_api_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")
    google_api_key: SecretStr = SecretStr("")
    groq_api_key: SecretStr = SecretStr("")
    together_api_key: SecretStr = SecretStr("")
    cerebras_api_key: SecretStr = SecretStr("")
    xai_api_key: SecretStr = SecretStr("")

    def key_for(self, provider: str) -> str:
        """Return the API key for a given provider name."""
        mapping: dict[str, SecretStr] = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "groq": self.groq_api_key,
            "together": self.together_api_key,
            "cerebras": self.cerebras_api_key,
            "xai": self.xai_api_key,
        }
        secret = mapping.get(provider)
        if secret is None:
            raise ValueError(f"Unknown LLM provider: {provider!r}")
        return secret.get_secret_value()


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")

    level: str = "INFO"
    format: str = "json"  # "json" | "console"

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}, got {v!r}")
        return upper

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v not in {"json", "console"}:
            raise ValueError(f"LOG_FORMAT must be 'json' or 'console', got {v!r}")
        return v


class DirectorySettings:
    """Computed project directory paths.

    All directories are derived from base_dir and are created automatically
    at startup.  These are not read from env vars — they are managed purely
    in code.
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir: Path = base_dir
        self.temp_dir: Path = base_dir / "temp"
        self.reports_dir: Path = base_dir / "reports"
        self.logs_dir: Path = base_dir / "logs"
        self.sample_data_dir: Path = base_dir / "sample_data"

    def create_all(self) -> None:
        for d in (self.temp_dir, self.reports_dir, self.logs_dir, self.sample_data_dir):
            d.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return (
            f"DirectorySettings("
            f"base={self.base_dir}, "
            f"temp={self.temp_dir}, "
            f"reports={self.reports_dir}, "
            f"logs={self.logs_dir}, "
            f"sample_data={self.sample_data_dir})"
        )


# ---------------------------------------------------------------------------
# Root settings
# ---------------------------------------------------------------------------


class Settings(BaseSettings):
    """Application-wide settings.

    Loaded from (in priority order, highest first):
      1. Actual environment variables
      2. .env file (relative to the working directory the app is started from)
      3. Defaults defined below

    Sub-settings groups use their own env_prefix so the var names stay flat:
      PRIMARY_DB_HOST, SUPABASE_URL, LOG_LEVEL, etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    app_env: str = Field(
        default="development",
        description="Runtime environment: development | staging | production",
    )
    debug: bool = False
    secret_key: SecretStr = SecretStr("dev-secret-key-change-in-production")
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Absolute path to the backend package root (used by tooling / migrations).
    # Defaults to the directory containing this file, which is backend/app/,
    # so we go up one level to get backend/.
    matrx_python_root: Path = Path(__file__).resolve().parent.parent

    # Cross-project roots — must be set in .env (no auto-resolved default).
    # ADMIN_PYTHON_ROOT=/absolute/path/to/admin-project/backend
    # ADMIN_TS_ROOT=/absolute/path/to/admin-project/frontend
    admin_python_root: Path | None = None
    admin_ts_root: Path | None = None

    # ------------------------------------------------------------------
    # Databases
    # ------------------------------------------------------------------
    # Primary database (env prefix: FLOW_MATRX_DB_)
    primary_db: DatabaseSettings = Field(
        default_factory=lambda: DatabaseSettings(
            _env_prefix="FLOW_MATRX_DB_",  # type: ignore[call-arg]
            _env_file=".env",  # type: ignore[call-arg]
        )
    )

    # Secondary database (env prefix: FLOW_MATRX_DB2_)
    secondary_db: DatabaseSettings = Field(
        default_factory=lambda: DatabaseSettings(
            _env_prefix="FLOW_MATRX_DB2_",  # type: ignore[call-arg]
            _env_file=".env",  # type: ignore[call-arg]
        )
    )

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------
    supabase: SupabaseSettings = Field(
        default_factory=lambda: SupabaseSettings(_env_file=".env")  # type: ignore[call-arg]
    )
    redis: RedisSettings = Field(
        default_factory=lambda: RedisSettings(_env_file=".env")  # type: ignore[call-arg]
    )
    llm: LLMSettings = Field(
        default_factory=lambda: LLMSettings(_env_file=".env")  # type: ignore[call-arg]
    )
    log: LogSettings = Field(
        default_factory=lambda: LogSettings(_env_file=".env")  # type: ignore[call-arg]
    )

    # ------------------------------------------------------------------
    # Directories (computed — excluded from pydantic validation)
    # ------------------------------------------------------------------
    # Declared as ClassVar so pydantic does not treat it as a model field.
    # Populated by the model_validator below.
    dirs: ClassVar[DirectorySettings]

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        valid = {"development", "staging", "production"}
        if v not in valid:
            raise ValueError(f"APP_ENV must be one of {valid}, got {v!r}")
        return v

    @model_validator(mode="after")
    def _build_dirs(self) -> Settings:
        Settings.dirs = DirectorySettings(self.matrx_python_root)
        Settings.dirs.create_all()
        return self


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
