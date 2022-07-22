from typing import (
    Generic,
    TypeVar,
    Union
)

import pymongo
from pydantic import (
    BaseModel,
    Field
)

from ..instance import database
from ..utils import (
    Direction,
    Indice,
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
            fields[field_name].allow_none = True

        return super().__new__(cls)

    @classmethod
    async def create_indices(cls):
        if cls.Config.indices is not None:
            indices = []
            for indice in cls.Config.indices:
                formatted_indice = BaseMixin.build_indice(cls, indice)
                pymongo_index = BaseMixin.build_pymongo_index(formatted_indice)
                indices.append(pymongo_index)

            await database.database[cls.__collection__].create_indexes(
                indexes=indices
            )

    @staticmethod
    def build_indice(cls, data: Union[Indice, tuple]) -> Indice:
        if isinstance(data, tuple):
            data = Indice(
                keys=[(data[0], data[1])],
                name=data[2] if len(data) > 2 else None,
                unique=data[3] if len(data) > 3 else None,
                background=data[4] if len(data) > 4 else None,
                sparse=data[5] if len(data) > 5 else None,
                bucket_size=data[6] if len(data) > 6 else None,
                min=data[7] if len(data) > 7 else None,
                max=data[8] if len(data) > 8 else None
            )

        if not isinstance(data, Indice):
            raise ValueError(
                f"Indice of type '{type(data)}' provided "
                f"to class '{cls.__name__}' is not supported"
            )

        if data.min is not None or data.max is not None:
            if data.keys[0][1] != Direction.GEO2D:
                raise ValueError(
                    f"Min/max value provided but direction "
                    f"is not GEO2D for class '{cls.__name__}'"
                )

        if data.bucket_size is not None:
            if data.keys[0][1] != Direction.GEOSPHERE:
                raise ValueError(
                    f"Bucket size value provided but direction "
                    f"is not GEOSPHERE for class '{cls.__name__}"
                )

        return data

    @staticmethod
    def build_pymongo_index(indice: Indice) -> pymongo.IndexModel:
        kwargs = {
            key: val for key, val in indice.__dict__.items()
            if not key.startswith("__") and val is not None
        }

        if "name" not in kwargs:
            kwargs["name"] = "_".join([key[0] for key in indice.keys]) + "_index"

        return pymongo.IndexModel(**kwargs)
