"""Forward migration runner for flow-matrx.

Usage
-----
Generate a migration from model/DB differences:
    python run_migrations.py make

Apply all pending migrations:
    python run_migrations.py apply

Roll back the last migration:
    python run_migrations.py rollback

Show migration status:
    python run_migrations.py status

Create a blank hand-written migration:
    python run_migrations.py empty --name my_change
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from matrx_orm import register_database_from_env, makemigrations, migrate, rollback, migration_status, create_empty

register_database_from_env(
    name="flow_matrx",
    env_prefix="DB",
    additional_schemas=[],
)

DATABASE = "flow_matrx"
MIGRATIONS_DIR = "migrations"


async def make(name: str | None = None) -> None:
    await makemigrations(DATABASE, MIGRATIONS_DIR, name=name)


async def apply() -> None:
    await migrate(DATABASE, MIGRATIONS_DIR)


async def rollback_last(steps: int = 1) -> None:
    await rollback(DATABASE, MIGRATIONS_DIR, steps=steps)


async def status() -> None:
    await migration_status(DATABASE, MIGRATIONS_DIR)


async def empty(name: str = "custom") -> None:
    await create_empty(DATABASE, MIGRATIONS_DIR, name=name)


def _usage() -> None:
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        _usage()

    command = args[0]

    match command:
        case "make":
            name_arg = args[1] if len(args) > 1 else None
            asyncio.run(make(name=name_arg))
        case "apply":
            asyncio.run(apply())
        case "rollback":
            steps = int(args[1]) if len(args) > 1 else 1
            asyncio.run(rollback_last(steps=steps))
        case "status":
            asyncio.run(status())
        case "empty":
            name_arg = args[1] if len(args) > 1 else "custom"
            asyncio.run(empty(name=name_arg))
        case _:
            print(f"Unknown command: {command!r}")
            _usage()
