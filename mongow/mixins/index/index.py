from __future__ import annotations

import pymongo

from ..utils import (
    Index,
    Direction
)
from ..base import BaseMixin
from ...instance import database


class IndexMixin(BaseMixin):

    @classmethod
    async def create_indices(cls):
        if cls.Config.indices is not None:
            indices = []
            for index in cls.Config.indices:
                formatted_indice = cls.build_index(index)
                pymongo_index = cls.build_pymongo_index(formatted_indice)
                indices.append(pymongo_index)

            await database.database[cls.__collection__].create_indexes(
                indexes=indices
            )

    @classmethod
    def build_index(cls, data: Index) -> Index:
        if not isinstance(data, Index):
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
    def build_pymongo_index(index: Index) -> pymongo.IndexModel:
        kwargs = {
            key: val for key, val in index.__dict__.items()
            if not key.startswith("__") and val is not None
        }

        if "name" not in kwargs:
            kwargs["name"] = "_".join([key[0] for key in index.keys]) + "_index"

        return pymongo.IndexModel(**kwargs)
