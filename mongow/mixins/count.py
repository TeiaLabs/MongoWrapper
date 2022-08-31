from typing import Any, Optional

from ..instance import database as client


class CountDocumentsMixin:
    __collection__ = "base"

    @classmethod
    async def count(cls, filters: Optional[dict[str, Any]] = None) -> int:
        col = client.database[cls.__collection__]
        c = await col.count_documents(filters if filters else {})
        return c

    @classmethod
    async def count_nested(
        cls, attribute_path: str, filters: Optional[dict[str, Any]] = None
    ) -> int:
        """
        Count root-level array attributes.
        
        TODO: count arbitrarily nested arrays.
        """
        col = client.database[cls.__collection__]
        c = col.aggregate(
            [
                {"$match": filters if filters else {}},
                {"$project": {"count": {"$size": f"${attribute_path}"}}},
            ]
        )
        docs = await c.to_list(1)
        return docs[0]["count"]
