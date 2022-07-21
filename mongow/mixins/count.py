from typing import (
    Optional,
    Union
)

from .base import (
    BaseMixin,
    T
)
from ..instance import database


class CountDocumentsMixin(BaseMixin):

    @classmethod
    async def count(
            cls,
            filters: Optional[Union[T, dict]] = None
    ) -> int:
        if filters is None:
            filters = {}

        if not isinstance(filters, dict):
            filters = filters.dict(
                exclude_unset=True,
                by_alias=True
            )

        col = database.database[cls.__collection__]
        return await col.count_documents(filters)
