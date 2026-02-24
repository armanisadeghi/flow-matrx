from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from app.steps.base import StepHandler
from app.steps.http_request import HttpRequestHandler
from app.steps.inline_code import InlineCodeHandler
from app.steps.llm_call import LLMCallHandler


class TestStepHandlerBase:
    """Test the base StepHandler class."""

    def test_validate_output_valid(self):
        """Test validate_output with valid JSON-serializable output."""
        handler = HttpRequestHandler()
        output = {"status_code": 200, "body": "test"}
        result = handler.validate_output(output)
        assert result == output

    def test_validate_output_too_large(self):
        """Test validate_output with output that's too large."""
        handler = HttpRequestHandler()
        # Create output larger than MAX_OUTPUT_SIZE
        large_output = {"data": "x" * (handler.MAX_OUTPUT_SIZE + 1)}
        with pytest.raises(ValueError, match="Step output too large"):
            handler.validate_output(large_output)

    def test_validate_output_non_serializable(self):
        """Test validate_output with non-JSON-serializable output."""
        handler = HttpRequestHandler()
        # Objects with methods are not JSON serializable
        class NonSerializable:
            def method(self): pass
        non_serializable = {"obj": NonSerializable()}
        with pytest.raises(ValueError, match="not JSON serializable"):
            handler.validate_output(non_serializable)


class TestHttpRequestHandler:
    """Test HTTP Request handler."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_http_get_request(self, mock_client_class):
        """Test basic GET request."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json = AsyncMock(return_value={"message": "success"})
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        handler = HttpRequestHandler()
        config = {"url": "https://api.example.com/data", "method": "GET"}
        context = {}

        result = await handler.execute(config, context)

        assert result["status_code"] == 200
        assert result["body"] == {"message": "success"}
        mock_client.request.assert_called_once_with(
            "GET", "https://api.example.com/data", headers={}, json=None
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_http_post_request(self, mock_client_class):
        """Test POST request with body."""
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Created"
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        handler = HttpRequestHandler()
        config = {
            "url": "https://api.example.com/users",
            "method": "POST",
            "body": {"name": "John"},
            "headers": {"Authorization": "Bearer token"}
        }
        context = {}

        result = await handler.execute(config, context)

        assert result["status_code"] == 201
        assert result["body"] == "Created"
        mock_client.request.assert_called_once_with(
            "POST", "https://api.example.com/users",
            headers={"Authorization": "Bearer token"},
            json={"name": "John"}
        )


class TestInlineCodeHandler:
    """Test Inline Code handler."""

    @pytest.mark.asyncio
    async def test_inline_code_basic_execution(self):
        """Test basic code execution that sets result."""
        handler = InlineCodeHandler()
        config = {"code": "result = input['value'] * 2"}
        context = {"input": {"value": 5}}

        result = await handler.execute(config, context)

        assert result["result"] == 10
        assert "context" in result
        assert "input" in result

    @pytest.mark.asyncio
    async def test_inline_code_missing_result(self):
        """Test code that doesn't set result variable."""
        handler = InlineCodeHandler()
        config = {"code": "x = 42"}  # Doesn't set result
        context = {"input": {}}

        with pytest.raises(ValueError, match="must set the 'result' variable"):
            await handler.execute(config, context)

    @pytest.mark.asyncio
    async def test_inline_code_with_context_access(self):
        """Test code that accesses context variables."""
        handler = InlineCodeHandler()
        config = {"code": "result = context['previous_step']['output'] + input['increment']"}
        context = {
            "previous_step": {"output": 10},
            "input": {"increment": 5}
        }

        result = await handler.execute(config, context)

        assert result["result"] == 15

    @pytest.mark.asyncio
    async def test_inline_code_safe_builtins(self):
        """Test that only safe builtins are available."""
        handler = InlineCodeHandler()
        # This should work - using safe builtins
        config = {"code": "result = len(str(sum([1, 2, 3])))"}
        context = {"input": {}}

        result = await handler.execute(config, context)

        assert result["result"] == 1  # len(str(6)) = 1


class TestLLMCallHandler:
    """Test LLM Call handler."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_openai_llm_call(self, mock_client_class):
        """Test OpenAI LLM call."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "Hello, world!"}}],
            "model": "gpt-4",
            "usage": {"total_tokens": 10}
        })
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        handler = LLMCallHandler()
        config = {
            "provider": "openai",
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.5
        }
        context = {}

        result = await handler.execute(config, context)

        assert result["content"] == "Hello, world!"
        assert result["model"] == "gpt-4"
        assert result["usage"] == {"total_tokens": 10}

    @pytest.mark.asyncio
    async def test_unsupported_provider(self):
        """Test unsupported LLM provider."""
        handler = LLMCallHandler()
        config = {"provider": "unsupported", "messages": []}
        context = {}

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            await handler.execute(config, context)