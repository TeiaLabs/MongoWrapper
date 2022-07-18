from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import pydantic
from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from .instance import database
from .mixins import IndexCreationMixin

T = TypeVar("T", bound="BaseMixin")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AllOptional(pydantic.main.ModelMetaclass, type):
    def __new__(cls, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(getattr(base, "__annotations__", {}))
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]  # type: ignore
        namespaces["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class BaseMixin(
    BaseModel,
    IndexCreationMixin,
    Generic[T],
    metaclass=AllOptional,
):
    __collection__ = "base"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str, ObjectId: str}

    @classmethod
    async def count(cls, filters: Optional[dict[str, Any]] = None) -> int:
        col = database.database[cls.__collection__]
        c = await col.count_documents(filters if filter else {})
        return c

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
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        if filters is None:
            filters = {}
        cursor = database.database[cls.__collection__].find(
            filters, {key: 1 for key in fields}
        )
        if order is not None:
            cursor = cursor.sort(order[0], 1 if order[1] else -1)
        return await cursor.skip(offset).to_list(length=offset + limit)

    @classmethod
    async def update(
        cls, filters: Dict[str, Any], data: Union[T, dict], operator: str
    ) -> int:
        if isinstance(data, dict):
            dict_data = data
        else:
            dict_data = data.dict(exclude_unset=True, by_alias=True)
            dict_data = {
                key: val for key, val in dict_data.items() if key not in filters
            }
        result = await database.database[cls.__collection__].update_one(
            filters, {operator: dict_data}
        )
        return result.modified_count

    @classmethod
    async def upsert(cls, filters: Dict[str, Any], data: T) -> int:
        dict_data = data.dict(exclude_unset=True, by_alias=True)
        dict_data = {key: val for key, val in dict_data.items() if key not in filters}
        result = await database.database[cls.__collection__].update_one(
            filters, {"$set": dict_data}, upsert=True, return_document=True
        )
        return result.modified_count

    @classmethod
    async def delete(cls, filters: Dict[str, Any]) -> int:
        result = await database.database[cls.__collection__].delete_many(filter=filters)
        return result.deleted_count

    @classmethod
    async def create_nested(
        cls, parent_id: ObjectId, child_name: str, data: T
    ) -> Optional[ObjectId]:
        result = await database.database[cls.__collection__].update_one(
            {"_id": parent_id}, {"$addToSet": {child_name: data.dict(by_alias=True)}}
        )
        if result.modified_count:
            return data.id
        return None

    @classmethod
    async def create_many(cls, data: List[T]) -> List[ObjectId]:
        result = await database.database[cls.__collection__].insert_many(
            [obj.dict(by_alias=True) for obj in data]
        )
        return result.inserted_ids
