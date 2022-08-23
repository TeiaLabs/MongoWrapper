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
    BaseConfig,
    PyObjectId,
)

T = TypeVar("T", bound="BaseMixin")


class BaseMixin(
    BaseModel,
    Generic[T]
):
    __collection__ = "base"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    Config = BaseConfig
