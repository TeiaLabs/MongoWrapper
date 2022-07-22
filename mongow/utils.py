import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    List,
    Optional,
    Tuple
)

from bson import ObjectId

from .instance import (
    database,
    Database,
    AsyncIOMotorClient
)


class Direction(Enum):
    ASCENDING = 0
    DESCENDING = 1
    GEO2D = 2
    GEOSPHERE = 3
    HASHED = 4
    TEXT = 5


@dataclass
class Indice:
    keys: List[Tuple[str, Direction]]
    name: str = None
    unique: bool = None
    background: bool = None
    sparse: bool = None
    bucket_size: int = None
    min: Any = None
    max: Any = None


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


def init_database(
        uri: Optional[str],
        username: Optional[str] = None,
        password: Optional[str] = None
) -> Database:
    schema = uri.split("/")[-1]
    schema = schema.split("?")[0]
    if username is None and password is None:
        database.client = AsyncIOMotorClient(uri)
    else:
        database.client = AsyncIOMotorClient(uri, username=username, password=password)

    database.database = database.client[schema]

    from .document import DocumentMixin

    coroutines = []
    for model in DocumentMixin.__subclasses__():
        coroutines.append(model.create_indices())

    try:
        loop = asyncio.get_running_loop()
        asyncio.ensure_future(asyncio.gather(*coroutines), loop=loop)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*coroutines))

    return database
