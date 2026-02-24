from __future__ import annotations

import pytest

from app.engine.templates import resolve_templates, extract_template_refs


class TestResolveTemplates:
    def test_plain_string_passthrough(self):
        assert resolve_templates("hello", {}) == "hello"

    def test_non_string_passthrough(self):
        assert resolve_templates(42, {}) == 42
        assert resolve_templates(None, {}) is None
        assert resolve_templates(True, {}) is True

    def test_single_template_returns_raw_value(self):
        scope = {"step_1": {"count": 42}}
        result = resolve_templates("{{step_1.count}}", scope)
        assert result == 42
        assert isinstance(result, int)

    def test_single_template_nested_dict(self):
        scope = {"step_1": {"users": [{"name": "Alice"}]}}
        result = resolve_templates("{{step_1.users}}", scope)
        assert result == [{"name": "Alice"}]
        assert isinstance(result, list)

    def test_single_template_preserves_type(self):
        scope = {"step_1": {"flag": False}}
        result = resolve_templates("{{step_1.flag}}", scope)
        assert result is False

    def test_embedded_template_returns_string(self):
        scope = {"step_1": {"name": "Alice"}}
        result = resolve_templates("Hello, {{step_1.name}}!", scope)
        assert result == "Hello, Alice!"
        assert isinstance(result, str)

    def test_dict_recursion(self):
        scope = {"step_1": {"url": "https://example.com"}}
        config = {"endpoint": "{{step_1.url}}", "method": "GET"}
        result = resolve_templates(config, scope)
        assert result == {"endpoint": "https://example.com", "method": "GET"}

    def test_list_recursion(self):
        scope = {"step_1": {"item": "value"}}
        config = ["{{step_1.item}}", "static"]
        result = resolve_templates(config, scope)
        assert result == ["value", "static"]

    def test_missing_key_raises(self):
        scope = {"step_1": {"a": 1}}
        with pytest.raises(KeyError):
            resolve_templates("{{step_1.nonexistent}}", scope)

    def test_missing_root_raises(self):
        scope = {}
        with pytest.raises(KeyError):
            resolve_templates("{{nonexistent.field}}", scope)

    def test_input_key(self):
        scope = {"input": {"email": "alice@example.com"}}
        result = resolve_templates("{{input.email}}", scope)
        assert result == "alice@example.com"

    def test_jinja_filter_falls_through_to_jinja(self):
        scope = {"step_1": {"name": "alice"}}
        result = resolve_templates("{{step_1.name | upper}}", scope)
        assert result == "ALICE"

    def test_list_index_access(self):
        scope = {"step_1": {"items": ["a", "b", "c"]}}
        result = resolve_templates("{{step_1.items.0}}", scope)
        assert result == "a"


class TestExtractTemplateRefs:
    def test_no_templates(self):
        assert extract_template_refs("plain string") == set()

    def test_single_ref(self):
        assert extract_template_refs("{{step_1.output}}") == {"step_1.output"}

    def test_multiple_refs(self):
        refs = extract_template_refs("{{step_1.a}} and {{step_2.b}}")
        assert refs == {"step_1.a", "step_2.b"}

    def test_refs_in_dict(self):
        config = {"url": "{{step_1.url}}", "body": {"name": "{{input.name}}"}}
        refs = extract_template_refs(config)
        assert refs == {"step_1.url", "input.name"}

    def test_refs_in_list(self):
        config = ["{{step_1.a}}", "static", "{{step_2.b}}"]
        refs = extract_template_refs(config)
        assert refs == {"step_1.a", "step_2.b"}

    def test_filter_stripped(self):
        refs = extract_template_refs("{{step_1.name | upper}}")
        assert refs == {"step_1.name"}
