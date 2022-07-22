from collections import abc
from typing import (
    Generic,
    Iterable,
    TypeVar,
    Union
)

from pydantic import (
    BaseModel,
    Field
)
from pymongo import (
    IndexModel,
    ASCENDING,
    DESCENDING
)

from ..instance import database
from ..utils import (
    ObjectId,
    PyObjectId
)

T = TypeVar("T", bound="BaseMixin")


class BaseMixin(
    BaseModel,
    Generic[T]
):
    __collection__ = "base"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed: bool = True
        use_enum_values: bool = True
        indices = None
        json_encoders = {
            ObjectId: str
        }

    def __new__(cls):
        self_dict = __class__.Config.__dict__
        subclass_dict = cls.Config.__dict__
        for key in self_dict:
            if key not in subclass_dict:
                if key == "arbitrary_types_allowed":
                    cls.Config.arbitrary_types_allowed = __class__.Config.arbitrary_types_allowed
                elif key == "use_enum_values":
                    cls.Config.use_enum_values = __class__.Config.use_enum_values
                elif key == "indices":
                    cls.Config.indices = __class__.Config.indices

        fields = cls.__dict__.get("__fields__", {})
        for field_name in fields:
            fields[field_name].required = False

        return super().__new__(cls)

    @classmethod
    async def create_indices(cls):
        if cls.Config.indices is not None:
            indices = []
            for indice in cls.Config.indices:
                if isinstance(indice, list):
                    inner_indices = []
                    indice_name = ""
                    for inner_indice in indice:
                        inner_indices.append((
                            inner_indice[0],
                            ASCENDING if inner_indice[1] else DESCENDING
                        ))
                        indice_name += inner_indice[0] + "_"

                    indices.append(IndexModel(inner_indices, name=indice_name[:-1]))
                else:
                    indices.append(
                        IndexModel([(
                            indice[0],
                            ASCENDING if indice[1] else DESCENDING
                        )], name=indice[0])
                    )

            await database.database[cls.__collection__].create_indexes(
                indexes=indices
            )
