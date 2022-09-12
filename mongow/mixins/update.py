from typing import Optional

from pymongo import UpdateOne
from pymongo.results import BulkWriteResult

from ..instance import database as client


class UpdateMixin:
    __collection__: str

    @classmethod
    async def bulk_update_one(
        cls,
        filters: list,
        documents: list,
        ops: Optional[list[str]] = None,
        upsert: bool = False,
    ) -> BulkWriteResult:
        """Update many documents with different values."""
        if ops is None:
            ops = ["$set"] * len(documents)
        result = await client.database[cls.__collection__].bulk_write(
            [
                UpdateOne(
                    filter=f,
                    update={op: d},
                    upsert=upsert,
                )
                for f, d, op in zip(filters, documents, ops)
            ]
        )
        return result
