import pytest
from bson import ObjectId

from tests.schemas import Fruit


@pytest.fixture
async def oids() -> list[ObjectId]:  # type: ignore
    fruits = [
        Fruit(name="Banana", taste="sweet"),
        Fruit(name="Strawberry", taste="bitter"),
    ]
    oids = await Fruit.batch_create(fruits)
    yield oids
    await Fruit.delete(filters={})


class TestUpdateMany:
    async def test_update_many(self, oids):
        data = Fruit(density=666)
        filters = {"_id": {"$in": oids}}
        fruits_updated = await Fruit.batch_update(data=data, filters=filters)
        assert fruits_updated == 2

    async def test_upsert_single(self, oids):
        data = Fruit(density=666)
        for oid in oids:
            filters = {"_id": oid}
            upserted_count = await Fruit.upsert(data=data, filters=filters)
            assert upserted_count == 1
