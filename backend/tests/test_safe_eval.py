from __future__ import annotations

import pytest

from app.engine.safe_eval import safe_eval


class TestSafeEval:
    def test_simple_comparison(self):
        assert safe_eval("1 > 0", {}) is True
        assert safe_eval("1 < 0", {}) is False

    def test_context_variable_access(self):
        ctx = {"step_1": {"count": 10}}
        assert safe_eval("step_1['count'] > 5", ctx) is True
        assert safe_eval("step_1['count'] == 10", ctx) is True

    def test_boolean_logic(self):
        ctx = {"a": True, "b": False}
        assert safe_eval("a and not b", ctx) is True
        assert safe_eval("a or b", ctx) is True
        assert safe_eval("not a", ctx) is False

    def test_arithmetic(self):
        ctx = {"x": 10, "y": 3}
        assert safe_eval("x + y", ctx) == 13
        assert safe_eval("x * y", ctx) == 30
        assert safe_eval("x % y", ctx) == 1

    def test_string_comparison(self):
        ctx = {"status": "active"}
        assert safe_eval("status == 'active'", ctx) is True
        assert safe_eval("status != 'inactive'", ctx) is True

    def test_in_operator(self):
        ctx = {"items": [1, 2, 3]}
        assert safe_eval("2 in items", ctx) is True
        assert safe_eval("5 in items", ctx) is False

    def test_invalid_syntax_raises(self):
        with pytest.raises(ValueError, match="Invalid expression syntax"):
            safe_eval("def foo(): pass", {})

    def test_disallowed_node_import(self):
        with pytest.raises((ValueError, NameError)):
            safe_eval("__import__('os')", {})

    def test_disallowed_node_lambda(self):
        with pytest.raises(ValueError, match="Disallowed"):
            safe_eval("(lambda: 1)()", {})

    def test_builtins_blocked(self):
        with pytest.raises((NameError, ValueError)):
            safe_eval("open('/etc/passwd')", {})

    def test_nested_dict_access(self):
        ctx = {"step_1": {"response": {"status_code": 200}}}
        assert safe_eval("step_1['response']['status_code'] == 200", ctx) is True

    def test_list_constant(self):
        assert safe_eval("[1, 2, 3]", {}) == [1, 2, 3]

    def test_dict_constant(self):
        result = safe_eval("{'a': 1}", {})
        assert result == {"a": 1}
