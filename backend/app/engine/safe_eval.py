"""Sandboxed expression evaluation for condition steps."""
from __future__ import annotations

import ast
from typing import Any

_ALLOWED_NODE_TYPES = {
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp,
    ast.Compare, ast.Call, ast.Attribute, ast.Subscript,
    ast.Name, ast.Constant, ast.List, ast.Dict, ast.Tuple,
    ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    ast.Is, ast.IsNot, ast.Add, ast.Sub, ast.Mult, ast.Div,
    ast.Mod, ast.Load, ast.Index,
}


def safe_eval(expression: str, context: dict[str, Any]) -> Any:
    """Evaluate a simple expression string in a restricted context."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    for node in ast.walk(tree):
        if type(node) not in _ALLOWED_NODE_TYPES:
            raise ValueError(
                f"Disallowed expression node type: {type(node).__name__}"
            )

    return eval(  # noqa: S307
        compile(tree, "<expression>", "eval"),
        {"__builtins__": {}},
        context,
    )
