from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from bson import ObjectId


class Direction(Enum):
    ASCENDING = 0
    DESCENDING = 1
    GEO2D = 2
    GEOSPHERE = 3
    HASHED = 4
    TEXT = 5


@dataclass
class Index:
    keys: list[tuple[str, Direction]]
    name: str = None
    unique: bool = None
    background: bool = None
    sparse: bool = None
    bucket_size: int = None
    min = None
    max = None


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
