from typing import (
    List,
    Union
)

from bson import ObjectId

from .base import (
    BaseMixin,
    T
)
from ..instance import database


class BatchModelMixin(BaseMixin):

    @classmethod
    async def batch_create(cls, data: List[T]) -> List[ObjectId]:
        result = await database.database[cls.__collection__].insert_many(
            [obj.dict(by_alias=True) for obj in data]
        )
        return result.inserted_ids

    @classmethod
    async def batch_update(cls, data: T, filters: Union[T, dict], operator: str = "$set") -> int:
        if not isinstance(filters, dict):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        dict_data = data.dict(
            exclude_unset=True,
            by_alias=True
        )
        dict_data = {
            key: val for key, val in dict_data.items() if key not in filters
        }

        result = await database.database[cls.__collection__].update_many(
            filters, {operator: dict_data}
        )
        return result.modified_count
