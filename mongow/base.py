import asyncio
from functools import wraps
from itertools import starmap
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
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseConfig, BaseModel, Field

from .instance import database
from .mixins import CountDocumentsMixin, IndexCreationMixin

T = TypeVar("T", bound="BaseMixin")
ObjOrDict = Union[T, dict[str, Any]]


def lost_event_loop(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RuntimeError as e:
            if str(e) == "Event loop is closed":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                if database.user and database.pwd:
                    database.client = AsyncIOMotorClient(
                        database.uri, username=username, password=password
                    )
                else:
                    database.client = AsyncIOMotorClient(database.uri)

                database.database = database.client[database.database.name]
                return await func(*args, **kwargs)

            raise e

    return wrap


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


BaseConfig.json_encoders = {
    PyObjectId: str,
    ObjectId: str,
}


class BaseMixin(
    BaseModel,
    CountDocumentsMixin,
    IndexCreationMixin,
    Generic[T],
    # metaclass=AllOptional,
):
    __collection__ = "base"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        fields = {
            "id": {"alias": "_id", "default_factory": PyObjectId}
        }

    @classmethod
    @lost_event_loop
    async def create(cls, data: T) -> ObjectId:
        result = await database.database[cls.__collection__].insert_one(
            data.dict(by_alias=True)
        )
        return result.inserted_id

    @classmethod
    def instantiate_obj(cls, key: str, value: Union[str, Any]) -> tuple[str, Any]:
        if isinstance(value, str):
            if key == "_id":
                return key, cls.__fields__["id"].type_(value)
            # TODO: get attr name by alias name
            # assume it is an _id and pop off its underscore
            # cls.schema(by_alias=True).get("properties").keys()
            # return key, typing.get_type_hints(cls)[search_key](value)
        return key, value

    @classmethod
    @lost_event_loop
    async def batch_create(cls, data: List[T]) -> List[ObjectId]:
        result = await database.database[cls.__collection__].insert_many(
            [obj.dict(by_alias=True) for obj in data]
        )
        return result.inserted_ids

    @classmethod
    @lost_event_loop
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
        else:
            filters = dict(starmap(cls.instantiate_obj, filters.items()))
        cursor = database.database[cls.__collection__].find(
            filters, {key: 1 for key in fields}
        )
        if order is not None:
            cursor = cursor.sort(order[0], 1 if order[1] else -1)
        objs = await cursor.skip(offset).to_list(length=limit)
        return objs

    @classmethod
    @lost_event_loop
    async def update(
            cls, filters: Dict[str, Any], data: Union[T, dict], operator: str = "$set", extra_params = None
    ) -> int:
        filters = dict(starmap(cls.instantiate_obj, filters.items()))
        if isinstance(data, dict):
            dict_data = data
        else:
            dict_data = data.dict(exclude_unset=True, by_alias=True)
            dict_data = {
                key: val for key, val in dict_data.items() if key not in filters
            }
            
        if extra_params is None:
            extra_params = {}
            
        result = await database.database[cls.__collection__].update_one(
            filters, {operator: dict_data}, **extra_params
        )
        return result.modified_count

    @classmethod
    @lost_event_loop
    async def batch_update(
            cls, data: ObjOrDict, filters: ObjOrDict, operator: str = "$set",
    ) -> int:
        if not isinstance(filters, dict):
            filters = filters.dict(exclude_unset=True, by_alias=True)
        if isinstance(data, dict):
            dict_data = data
        else:
            dict_data = data.dict(exclude_unset=True, by_alias=True)
        dict_data = {
            key: val for key, val in dict_data.items() if key not in filters
        }
        result = await database.database[cls.__collection__].update_many(
            filters, {operator: dict_data}
        )
        return result.modified_count

    @classmethod
    @lost_event_loop
    async def upsert(cls, data: ObjOrDict, filters: ObjOrDict) -> int:
        if not isinstance(filters, dict):
            filters = filters.dict(exclude_unset=True, by_alias=True)
        if isinstance(data, dict):
            dict_data = data
        else:
            dict_data = data.dict(exclude_unset=True, by_alias=True)
        dict_data = {key: val for key, val in dict_data.items() if key not in filters}
        result = await database.database[cls.__collection__].update_one(
            filters, {"$set": dict_data}, upsert=True
        )
        return result.modified_count

    @classmethod
    @lost_event_loop
    async def delete(cls, filters: Dict[str, Any]) -> int:
        result = await database.database[cls.__collection__].delete_many(filter=filters)
        return result.deleted_count

    @classmethod
    @lost_event_loop
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
    @lost_event_loop
    async def create_many(cls, data: List[T]) -> List[ObjectId]:
        result = await database.database[cls.__collection__].insert_many(
            [obj.dict(by_alias=True) for obj in data]
        )
        return result.inserted_ids
