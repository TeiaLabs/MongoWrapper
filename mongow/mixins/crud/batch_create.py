from __future__ import annotations

from typing import Type

from ..base import (
    BaseMixin,
    T
)
from ..results import BatchCreateResult
from ..utils import PyObjectId
from ...instance import database


class BatchCreateMixin(BaseMixin):

    @classmethod
    async def batch_create(
            cls: Type[T],
            data: list[T]
    ) -> BatchCreateResult:
        result = await database.database[cls.__collection__].insert_many(
            [obj.dict(by_alias=True) for obj in data]
        )
        return BatchCreateResult(
            inserted_ids=[
                PyObjectId(inserted_id)
                for inserted_id in result.inserted_ids
            ]
        )
