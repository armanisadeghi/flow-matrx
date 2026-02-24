from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = Field(default="dev-secret-key")
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Database connection — individual vars consumed by register_database_from_env
    # with env_prefix="DB". Set these in .env:
    #   DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    # DB_PROTOCOL is optional (defaults to postgresql).
    redis_url: str = "redis://localhost:6379"

    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    openai_api_key: str = ""
    anthropic_api_key: str = ""


settings = Settings()
