"""Tests for the function registry and FunctionCall step handler."""

from __future__ import annotations

import pytest

from app.engine.function_registry import (
    FunctionNotFoundError,
    FunctionRegistry,
    FunctionValidationError,
    register_function,
)
from app.steps.function_call import FunctionCallHandler


# ---------------------------------------------------------------------------
# Function Registry
# ---------------------------------------------------------------------------

class TestFunctionRegistry:
    def test_register_callable(self) -> None:
        reg = FunctionRegistry()

        async def my_func(config: dict, context: dict) -> dict:
            return {"result": config["x"] * 2}

        reg.register_callable("my_func", my_func)
        assert reg.has("my_func")
        assert reg.get("my_func") is my_func

    def test_register_with_metadata(self) -> None:
        reg = FunctionRegistry()

        async def enricher(config: dict, context: dict) -> dict:
            return {"enriched": True}

        reg.register_callable(
            "enricher",
            enricher,
            metadata={"description": "Enriches data", "category": "data"},
        )
        meta = reg.get_metadata("enricher")
        assert meta["description"] == "Enriches data"

    def test_get_nonexistent_raises(self) -> None:
        reg = FunctionRegistry()
        with pytest.raises(FunctionNotFoundError):
            reg.get("nonexistent")

    def test_has_returns_false(self) -> None:
        reg = FunctionRegistry()
        assert not reg.has("nope")

    def test_unregister(self) -> None:
        reg = FunctionRegistry()

        async def f(config: dict, context: dict) -> dict:
            return {}

        reg.register_callable("f", f)
        assert reg.has("f")
        reg.unregister("f")
        assert not reg.has("f")

    def test_clear(self) -> None:
        reg = FunctionRegistry()

        async def f(config: dict, context: dict) -> dict:
            return {}

        reg.register_callable("f", f)
        reg.clear()
        assert reg.registered_names == []

    def test_sync_function_rejected(self) -> None:
        reg = FunctionRegistry()

        def sync_func(config: dict, context: dict) -> dict:
            return {}

        with pytest.raises(FunctionValidationError, match="async"):
            reg.register_callable("sync", sync_func)

    def test_non_callable_rejected(self) -> None:
        reg = FunctionRegistry()
        with pytest.raises(FunctionValidationError, match="not callable"):
            reg.register_callable("bad", "not a function")

    def test_get_catalog(self) -> None:
        reg = FunctionRegistry()

        async def a(config: dict, context: dict) -> dict:
            return {}

        async def b(config: dict, context: dict) -> dict:
            return {}

        reg.register_callable("alpha", a, metadata={"description": "Alpha func"})
        reg.register_callable("beta", b, metadata={"description": "Beta func"})

        catalog = reg.get_catalog()
        assert len(catalog) == 2
        names = [entry["name"] for entry in catalog]
        assert "alpha" in names
        assert "beta" in names

    def test_register_many(self) -> None:
        reg = FunctionRegistry()
        # Use a real importable path
        with pytest.raises(FunctionNotFoundError):
            reg.register_many([
                {"import_path": "nonexistent.module.func"},
            ])


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------

class TestRegisterFunctionDecorator:
    def test_decorator_registers(self) -> None:
        from app.engine.function_registry import function_registry

        @register_function("test_decorated")
        async def my_decorated(config: dict, context: dict) -> dict:
            return {"decorated": True}

        assert function_registry.has("test_decorated")
        assert function_registry.get("test_decorated") is my_decorated

        # Cleanup
        function_registry.unregister("test_decorated")


# ---------------------------------------------------------------------------
# FunctionCallHandler
# ---------------------------------------------------------------------------

class TestFunctionCallHandler:
    @pytest.mark.asyncio
    async def test_execute_registered_function(self) -> None:
        from app.engine.function_registry import function_registry

        async def double(config: dict, context: dict) -> dict:
            return {"result": config.get("value", 0) * 2}

        function_registry.register_callable("double", double)
        try:
            handler = FunctionCallHandler()
            config = {"function_name": "double", "args": {"value": 21}}
            result = await handler.execute(config, {})
            assert result["result"] == 42
        finally:
            function_registry.unregister("double")

    @pytest.mark.asyncio
    async def test_execute_unregistered_raises(self) -> None:
        handler = FunctionCallHandler()
        config = {"function_name": "does_not_exist", "args": {}}
        with pytest.raises(FunctionNotFoundError):
            await handler.execute(config, {})
