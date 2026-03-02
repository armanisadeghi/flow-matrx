# ruff: noqa: I001, F401 — bootstrap must be imported first and is used for side effects
import app.bootstrap  # configures matrx_utils/LazySettings before any ORM import
from matrx_orm.schema_builder import run_schema_generation

run_schema_generation("matrx_orm.yaml")
