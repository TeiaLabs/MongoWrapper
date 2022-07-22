from itertools import starmap
from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Union
)

from bson import ObjectId

from .base import (
    BaseMixin,
    T
)
from ..instance import database


class ModelMixin(BaseMixin):

    @classmethod
    def instantiate_obj(cls, key: str, value: Union[str, Any]) -> tuple[str, Any]:
        if isinstance(value, str):
            if key == "_id":
                return key, ObjectId(value)
            # TODO: get attr name by alias name
            # assume it is an _id and pop off its underscore
            # cls.schema(by_alias=True).get("properties").keys()
            # return key, typing.get_type_hints(cls)[search_key](value)
        return key, value

    @classmethod
    async def create(cls, data: T) -> ObjectId:
        result = await database.database[cls.__collection__].insert_one(
            data.dict(by_alias=True)
        )
        return result.inserted_id

    @classmethod
    async def read(
            cls,
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
        else:
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
            upsert=True,
            return_document=True
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
