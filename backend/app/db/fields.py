# Hand-authored. Never touched by the generator.
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Generic, TypeVar

from matrx_orm import JSONBField

T = TypeVar("T")


class TypedJSONBField(JSONBField, Generic[T]):  # type: ignore[misc]  # noqa: UP046
    """JSONBField that deserializes into a typed dataclass.

    Pass the dataclass type as the first positional argument. All remaining
    kwargs are forwarded to JSONBField unchanged.

    The dataclass type is also used as the default factory so that
    null=False fields always get a fresh empty instance rather than a
    shared mutable dict.

    Usage:
        field = TypedJSONBField(MyType, null=False)
        field = TypedJSONBField(MyType)           # nullable
    """

    # Descriptor stub: instance access resolves to T, class access to the field itself.
    def __get__(self, obj: object | None, objtype: type | None = None) -> T:  # type: ignore[override]
        return super().__get__(obj, objtype)  # type: ignore[return-value]

    def __init__(self, dataclass_type: type[T], **kwargs: Any) -> None:
        self._dataclass_type = dataclass_type
        if "default" not in kwargs:
            kwargs["default"] = dataclass_type
        super().__init__(**kwargs)

    def to_python(self, value: Any) -> T | None:
        raw = super().to_python(value)
        if raw is None:
            return None
        if isinstance(raw, self._dataclass_type):
            return raw
        if isinstance(raw, dict):
            return self._dataclass_type(**raw)
        return raw  # type: ignore[return-value]

    def get_db_prep_value(self, value: Any) -> Any:
        if is_dataclass(value) and not isinstance(value, type):
            return super().get_db_prep_value(asdict(value))
        return super().get_db_prep_value(value)
