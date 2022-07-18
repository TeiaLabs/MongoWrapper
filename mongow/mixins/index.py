from typing import Optional

from pymongo import IndexModel


class IndexCreationMixin:
    __collection__: str
    __indices__: Optional[list[IndexModel]] = None

    @classmethod
    async def create_indices(cls, db):
        if not cls.__indices__:
            return
        await db[cls.__collection__].create_indexes(cls.__indices__)
