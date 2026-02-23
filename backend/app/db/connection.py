from __future__ import annotations

from matrx_orm import MatrxORM

from app.config import settings

# Matrx-ORM manages the asyncpg connection pool internally.
# asyncpg 0.31.x is used as the underlying driver.

_orm: MatrxORM | None = None


async def init_db() -> None:
    """Initialize Matrx-ORM and the underlying asyncpg connection pool."""
    global _orm
    _orm = MatrxORM(settings.database_url, min_size=2, max_size=10)
    await _orm.connect()


async def close_db() -> None:
    """Close the Matrx-ORM connection pool."""
    global _orm
    if _orm is not None:
        await _orm.disconnect()
        _orm = None


def get_db() -> MatrxORM:
    """Return the active Matrx-ORM instance. Used for dependency injection."""
    if _orm is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    return _orm
