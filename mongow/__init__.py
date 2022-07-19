from typing import Optional

from .instance import (
    database,
    Database,
    AsyncIOMotorClient
)

from .base import (
    BaseMixin,
    PyObjectId,
    AllOptional
)


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
    return database
