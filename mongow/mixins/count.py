from typing import Any, Optional

from ..instance import database as client


class CountDocumentsMixin():
    __collection__ = "base"

    @classmethod
    async def count(cls, filters: Optional[dict[str, Any]] = None) -> int:
        col = client.database[cls.__collection__]
        c = await col.count_documents(filters if filter else {})
        return c
