from __future__ import annotations

from typing import Type

from ..base import (
    BaseMixin,
    T
)
from ..results import DeleteResult
from ...instance import database


class DeleteMixin(BaseMixin):

    @classmethod
    async def delete(
            cls: Type[T],
            filters: T | dict = None
    ) -> DeleteResult:
        if filters is None:
            filters = {}
        elif isinstance(filters, cls):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        result = await database.database[cls.__collection__].delete_many(
            filter=filters
        )
        return DeleteResult(
            deleted_count=result.deleted_count
        )
