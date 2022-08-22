from __future__ import annotations

from ..base import (
    BaseMixin,
    T
)
from ...instance import database


class AggregateMixin(BaseMixin):

    @classmethod
    async def aggregate(
            cls,
            pipeline: list[dict],
            raw: bool = True
    ) -> list[T]:
        objs = await database.database[cls.__collection__].aggregate(
            pipeline
        ).to_list(length=None)

        if raw:
            return objs
        return [cls.construct(**obj) for obj in objs]
