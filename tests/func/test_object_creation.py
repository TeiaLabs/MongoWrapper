import pytest
from bson import ObjectId

from tests.schemas import Fruit


@pytest.mark.asyncio
async def test_create_obj(db):
    f = Fruit(name="Banana", taste="sweet")
    oid = await Fruit.create(f)
    assert oid is not None
    assert isinstance(oid, ObjectId)
