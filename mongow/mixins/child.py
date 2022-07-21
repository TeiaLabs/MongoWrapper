from bson import ObjectId

from .base import (
    BaseMixin,
    T
)
from ..instance import database


class ChildMixin(BaseMixin):

    @classmethod
    async def insert_child(
            cls,
            parent_id: ObjectId,
            child_name: str,
            data: T
    ) -> int:
        result = await database.database[cls.__collection__].update_one(
            {"_id": parent_id},
            {"$addToSet": {
                child_name: data.dict(
                    by_alias=True
                )
            }}
        )
        return result.modified_count
