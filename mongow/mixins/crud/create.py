from __future__ import annotations

from ..base import (
    BaseMixin,
    T
)
from ..results import CreateResult
from ..utils import PyObjectId
from ...instance import database


class CreateMixin(BaseMixin):

    @classmethod
    async def create(cls, data: T) -> CreateResult:
        result = await database.database[cls.__collection__].insert_one(
            data.dict(by_alias=True)
        )
        return CreateResult(
            inserted_id=PyObjectId(result.inserted_id)
        )
