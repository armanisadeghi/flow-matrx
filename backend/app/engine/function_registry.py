"""Registry for user-defined Python functions that can be invoked as step handlers.

Functions are registered by dotted import path and called with (config, context).
They must be async callables that return a dict.

Usage:

    # Register via decorator:
    @register_function("my_module.my_func")
    async def my_func(config: dict, context: dict) -> dict:
        return {"result": config["x"] * 2}

    # Register via import path:
    function_registry.register("my_package.tasks.process_data")

    # Register from a config dict (e.g. loaded from YAML/DB):
    function_registry.register_many([
        {"name": "process_data", "import_path": "my_package.tasks.process_data"},
        {"name": "enrich_user", "import_path": "my_package.tasks.enrich_user"},
    ])
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable, Coroutine
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

FunctionType = Callable[[dict[str, Any], dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


class FunctionNotFoundError(Exception):
    pass


class FunctionValidationError(Exception):
    pass


class FunctionRegistry:
    def __init__(self) -> None:
        self._functions: dict[str, FunctionType] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    @property
    def registered_names(self) -> list[str]:
        return sorted(self._functions.keys())

    def register(
        self,
        import_path: str,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a function by its dotted import path.

        Args:
            import_path: Dotted path like "my_package.module.function_name"
            name: Display name.  Defaults to the function's __name__.
            metadata: Optional metadata (description, input_schema, etc.)
        """
        func = self._import_callable(import_path)
        func_name = name or func.__name__
        self._functions[func_name] = func
        self._metadata[func_name] = metadata or {}
        logger.info("Registered function", name=func_name, import_path=import_path)

    def register_callable(
        self,
        name: str,
        func: FunctionType,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register an already-imported callable directly."""
        if not callable(func):
            raise FunctionValidationError(f"{name!r} is not callable")
        if not inspect.iscoroutinefunction(func):
            raise FunctionValidationError(
                f"{name!r} must be an async function (async def)"
            )
        self._functions[name] = func
        self._metadata[name] = metadata or {}

    def register_many(self, entries: list[dict[str, Any]]) -> None:
        """Bulk-register from a list of config dicts.

        Each dict must have 'import_path' and optionally 'name' and 'metadata'.
        """
        for entry in entries:
            self.register(
                import_path=entry["import_path"],
                name=entry.get("name"),
                metadata=entry.get("metadata"),
            )

    def get(self, name: str) -> FunctionType:
        func = self._functions.get(name)
        if func is None:
            raise FunctionNotFoundError(
                f"Function {name!r} not registered.  "
                f"Available: {', '.join(self.registered_names) or '(none)'}"
            )
        return func

    def has(self, name: str) -> bool:
        return name in self._functions

    def get_metadata(self, name: str) -> dict[str, Any]:
        return self._metadata.get(name, {})

    def get_catalog(self) -> list[dict[str, Any]]:
        """Return metadata for all registered functions (for the frontend palette)."""
        catalog: list[dict[str, Any]] = []
        for name in self.registered_names:
            meta = self._metadata.get(name, {})
            catalog.append({
                "name": name,
                "description": meta.get("description", ""),
                "input_schema": meta.get("input_schema", {}),
                "output_schema": meta.get("output_schema", {}),
                "category": meta.get("category", "custom"),
            })
        return catalog

    def unregister(self, name: str) -> None:
        self._functions.pop(name, None)
        self._metadata.pop(name, None)

    def clear(self) -> None:
        self._functions.clear()
        self._metadata.clear()

    @staticmethod
    def _import_callable(import_path: str) -> FunctionType:
        """Import a callable from a dotted path like 'package.module.func'."""
        parts = import_path.rsplit(".", 1)
        if len(parts) != 2:
            raise FunctionValidationError(
                f"Invalid import path {import_path!r}: expected 'module.function'"
            )
        module_path, func_name = parts
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            raise FunctionNotFoundError(
                f"Cannot import module {module_path!r}: {exc}"
            ) from exc

        func = getattr(module, func_name, None)
        if func is None:
            raise FunctionNotFoundError(
                f"Module {module_path!r} has no attribute {func_name!r}"
            )
        if not callable(func):
            raise FunctionValidationError(
                f"{import_path!r} is not callable"
            )
        if not inspect.iscoroutinefunction(func):
            raise FunctionValidationError(
                f"{import_path!r} must be an async function (async def)"
            )
        return func


# Singleton
function_registry = FunctionRegistry()


def register_function(
    name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Callable[[FunctionType], FunctionType]:
    """Decorator to register an async function as a workflow step.

    Usage:
        @register_function("my_processor")
        async def my_processor(config: dict, context: dict) -> dict:
            return {"result": "processed"}
    """

    def decorator(func: FunctionType) -> FunctionType:
        func_name = name or func.__name__
        function_registry.register_callable(func_name, func, metadata)
        return func

    return decorator
