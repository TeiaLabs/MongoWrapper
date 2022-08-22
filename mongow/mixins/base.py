from __future__ import annotations

from typing import (
    Generic,
    TypeVar
)

from pydantic import (
    BaseModel,
    Field
)

from .utils import (
    Index,
    PyObjectId
)

T = TypeVar("T", bound="BaseMixin")


class BaseMixin(
    BaseModel,
    Generic[T]
):
    __collection__ = "base"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed: bool = True
        use_enum_values: bool = True
        indices: list[Index] = None
