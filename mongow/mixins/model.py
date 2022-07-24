from itertools import starmap
from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from bson import ObjectId

from .base import (
    BaseMixin,
    T
)
from ..instance import database


class ModelMixin(BaseMixin):

    @classmethod
    async def create(cls, data: T) -> ObjectId:
        if not data.id:
           data.id = ObjectId() 
        result = await database.database[cls.__collection__].insert_one(
            data.dict(by_alias=True)
        )
        return result.inserted_id

    @classmethod
    async def read(
        cls: Type[T],
        fields: Iterable[str] = tuple(),
        order: Optional[Tuple[str, bool]] = None,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[Union[T, dict]] = None,
        construct_object: bool = False
    ) -> List[T]:
        if filters is None:
            filters = {}
        elif isinstance(filters, cls):
            filters = filters.dict(exclude_unset=True, by_alias=True)
        elif isinstance(filters, dict):
            filters = dict(starmap(cls.instantiate_obj, filters.items()))

        cursor = database.database[cls.__collection__].find(
            filters, {key: 1 for key in fields}
        )

        if order is not None:
            cursor = cursor.sort(order[0], 1 if order[1] else -1)

        objs = await cursor.skip(offset).to_list(length=offset + limit)
        if construct_object:
            return [cls.construct(**obj) for obj in objs]
        return objs

    @classmethod
    async def aggregate(cls, pipeline, construct_object: bool = False) -> Any:
        objs = await database.database[cls.__collection__].aggregate(
            pipeline
        ).to_list(length=None)

        if construct_object:
            return [cls.construct(**obj) for obj in objs]
        return objs

    @classmethod
    async def update(
        cls,
        data: T,
        filters: Union[T, dict],
        operator: str = "$set"
    ) -> int:
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

        result = await database.database[cls.__collection__].update_one(
            filters, {operator: dict_data}
        )
        return result.modified_count

    @classmethod
    async def upsert(cls, data: T, filters: Union[T, dict]) -> int:
        if not isinstance(filters, dict):
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
        return result.modified_count

    @classmethod
    async def delete(cls, filters: Optional[Union[T, dict]] = None) -> int:
        if filters is None:
            filters = {}

        if not isinstance(filters, dict):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        result = await database.database[cls.__collection__].delete_many(
            filter=filters
        )
        return result.deleted_count
