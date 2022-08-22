from __future__ import annotations

from typing import Type

from ..base import (
    BaseMixin,
    T
)
from ..results import UpdateResult
from ...instance import database


class UpdateMixin(BaseMixin):

    @classmethod
    async def update(
            cls: Type[T],
            data: T,
            filters: T | dict,
            operator: str = "$set"
    ) -> UpdateResult:
        if isinstance(filters, cls):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        dict_data = data.dict(
            exclude_unset=True,
            by_alias=True
        )
        dict_data = {
            key: val for key, val in dict_data.items()
            if key not in filters
        }

        result = await database.database[cls.__collection__].update_one(
            filters, {operator: dict_data}
        )
        return UpdateResult(
            matched_count=result.matched_count,
            modified_count=result.modified_count
        )
