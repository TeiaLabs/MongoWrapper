from __future__ import annotations

from typing import Type

from ..base import (
    BaseMixin,
    T
)
from ..results import UpsertResult
from ...instance import database


class UpsertMixin(BaseMixin):

    @classmethod
    async def upsert(
            cls: Type[T],
            data: T,
            filters: T | dict
    ) -> UpsertResult:
        if isinstance(filters, cls):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        dict_data = data.dict(
            exclude_unset=True,
            by_alias=True
        )
        dict_data = {key: val for key, val in dict_data.items() if key not in filters}

        result = await database.database[cls.__collection__].update_one(
            filters,
            {"$set": dict_data},
            upsert=True
        )

        return UpsertResult(
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_id=result.upserted_id
        )
