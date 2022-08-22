from __future__ import annotations

from typing import (
    List,
    Type,
)

from ..base import (
    BaseMixin,
    T
)
from ...instance import database


class ReadMixin(BaseMixin):

    @classmethod
    async def read(
            cls: Type[T],
            filters: T | dict = None,
            fields: tuple[str] = tuple(),
            order: tuple[str, bool] = None,
            offset: int = 0,
            limit: int = 100,
            raw: bool = True
    ) -> List[T | dict]:
        if filters is None:
            filters = {}
        elif isinstance(filters, cls):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        cursor = database.database[cls.__collection__].find(
            filters, {key: 1 for key in fields}
        )

        if order is not None:
            cursor = cursor.sort(order[0], 1 if order[1] else -1)

        objs = await cursor.skip(offset).to_list(length=offset + limit)
        if raw:
            return objs

        return [cls.construct(**obj) for obj in objs]
