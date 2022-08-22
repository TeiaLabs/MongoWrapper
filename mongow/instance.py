import asyncio
from typing import (
    Optional
)

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=Singleton):
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


database = Database()


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

    asyncio.wait_for(asyncio.gather(*coroutines), 30)

    return database
