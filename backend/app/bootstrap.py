"""Matrx ecosystem bootstrap.

Import this module once — at the very top of any entry point — before any
matrx_utils or matrx_orm code is imported.  It configures the matrx_utils
LazySettings singleton using the application's pydantic Settings object,
so that every part of the matrx ecosystem has access to the same values.

    # Entry points (scripts, CLI tools, generate.py, etc.):
    import app.bootstrap  # noqa: F401 — must be first import

    # FastAPI lifespan / main.py — call it explicitly if you prefer:
    from app.bootstrap import bootstrap
    bootstrap()

The module is idempotent: calling it multiple times is safe.
"""
from __future__ import annotations

import os

_bootstrapped = False


def bootstrap() -> None:
    """Configure matrx_utils with the application settings.

    Pulls values from the pydantic Settings singleton and writes the ones
    matrx_utils/matrx_orm need into os.environ so their LazySettings
    singleton can find them.  Also calls configure_settings() so that
    attribute-style access (settings.SOME_KEY) works on the LazySettings
    object directly.

    Safe to call multiple times — subsequent calls are no-ops.
    """
    global _bootstrapped
    if _bootstrapped:
        return

    # --- Import here to avoid circular import at module level ---------------
    from app.config import settings as app_settings  # noqa: I001
    from matrx_utils.conf import settings as matrx_settings, configure_settings

    # -------------------------------------------------------------------------
    # 1. Write values into os.environ so that LazySettings env-cache picks them
    #    up regardless of whether configure_settings has been called yet.
    #
    #    We only setdefault — real environment variables always win.
    # -------------------------------------------------------------------------
    _env_map: dict[str, str] = {
        # matrx_utils FileHandler needs this to resolve base_dir
        "BASE_DIR": str(app_settings.matrx_python_root),

        # matrx_orm schema generator uses these directly
        "MATRX_PYTHON_ROOT": str(app_settings.matrx_python_root),

        # Cross-project roots (only written if set in .env)
        **({} if app_settings.admin_python_root is None else {"ADMIN_PYTHON_ROOT": str(app_settings.admin_python_root)}),
        **({} if app_settings.admin_ts_root is None else {"ADMIN_TS_ROOT": str(app_settings.admin_ts_root)}),

        # Standard app values — convenient for any matrx tool that needs them
        "APP_ENV": app_settings.app_env,
        "LOG_LEVEL": app_settings.log.level,
        "LOG_FORMAT": app_settings.log.format,
    }

    for key, value in _env_map.items():
        os.environ.setdefault(key, value)

    # -------------------------------------------------------------------------
    # 2. Configure the LazySettings singleton with the full pydantic Settings
    #    object so attribute-style access works (matrx_settings.SOME_ATTR).
    #
    #    LazySettings raises RuntimeError if already configured, so we check.
    # -------------------------------------------------------------------------
    if not matrx_settings._configured:
        configure_settings(
            _MatrxSettingsAdapter(app_settings),
            env_first=True,   # env vars win — consistent with pydantic-settings priority
        )

    _bootstrapped = True


class _MatrxSettingsAdapter:
    """Thin adapter that makes a pydantic Settings object look like a flat
    settings object to matrx_utils LazySettings.

    LazySettings calls getattr(settings_object, name) with UPPER_SNAKE_CASE
    names.  This adapter maps those names to the right values on the pydantic
    Settings hierarchy, covering every name matrx_utils currently uses.
    """

    def __init__(self, app_settings: object) -> None:
        self._s = app_settings

    def __getattr__(self, name: str) -> object:
        s = object.__getattribute__(self, "_s")

        # Canonical flat name → pydantic attribute path
        match name.upper():
            # Core paths
            case "BASE_DIR":
                return str(s.matrx_python_root)
            case "MATRX_PYTHON_ROOT":
                return str(s.matrx_python_root)
            case "ADMIN_PYTHON_ROOT":
                return str(s.admin_python_root) if s.admin_python_root is not None else ""
            case "ADMIN_TS_ROOT":
                return str(s.admin_ts_root) if s.admin_ts_root is not None else ""

            # App
            case "APP_ENV" | "ENVIRONMENT":
                return s.app_env
            case "DEBUG":
                return s.debug
            case "SECRET_KEY":
                return s.secret_key.get_secret_value()

            # Logging
            case "LOG_LEVEL":
                return s.log.level
            case "LOG_FORMAT":
                return s.log.format

            # Primary DB (flat names matrx_orm may look for)
            case "DB_HOST":
                return s.primary_db.host
            case "DB_PORT":
                return str(s.primary_db.port)
            case "DB_NAME":
                return s.primary_db.name
            case "DB_USER":
                return s.primary_db.user
            case "DB_PASSWORD":
                return s.primary_db.password.get_secret_value()
            case "DB_PROTOCOL":
                return s.primary_db.protocol

            # Supabase
            case "SUPABASE_URL":
                return s.supabase.url
            case "SUPABASE_JWT_SECRET":
                return s.supabase.jwt_secret.get_secret_value()

            # Redis
            case "REDIS_URL":
                return s.redis.url

            # LLM keys
            case "OPENAI_API_KEY":
                return s.llm.openai_api_key.get_secret_value()
            case "ANTHROPIC_API_KEY":
                return s.llm.anthropic_api_key.get_secret_value()
            case "GOOGLE_API_KEY":
                return s.llm.google_api_key.get_secret_value()
            case "GROQ_API_KEY":
                return s.llm.groq_api_key.get_secret_value()
            case "TOGETHER_API_KEY":
                return s.llm.together_api_key.get_secret_value()
            case "CEREBRAS_API_KEY":
                return s.llm.cerebras_api_key.get_secret_value()
            case "XAI_API_KEY":
                return s.llm.xai_api_key.get_secret_value()

            case _:
                raise AttributeError(f"_MatrxSettingsAdapter has no mapping for {name!r}")


# ---------------------------------------------------------------------------
# Auto-bootstrap on import — just `import app.bootstrap` is enough.
# ---------------------------------------------------------------------------
bootstrap()
