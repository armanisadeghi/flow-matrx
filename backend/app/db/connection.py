# Database registration is handled by importing the db package.
# This triggers db/__init__.py which calls register_database_from_env.
import db  # noqa: F401 — side-effect import registers the database
