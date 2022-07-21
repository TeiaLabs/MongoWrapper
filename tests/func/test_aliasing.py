import pytest

from tests.schemas import Fruit


@pytest.fixture
async def oid():
    f = Fruit(name="Banana", taste="sweet")
    oid = await Fruit.create(f)
    return oid


class TestRetrieveAndInstantiate:

    async def test_alias_oid(self, oid):
        filters = dict(_id=oid)
        await self.check_response(filters)

    async def test_alias_str(self, oid):
        filters = dict(_id=str(oid))
        await self.check_response(filters)

    async def test_name_oid(self, oid):
        filters = dict(id=oid)
        await self.check_response(filters)

    async def test_name_str(self, oid):
        filters = dict(id=str(oid))
        await self.check_response(filters)

    @staticmethod
    async def check_response(filters):
        objs = await Fruit.read(filters=filters)
        assert len(objs) == 1
        f = Fruit(**objs[0])
        assert isinstance(f, Fruit)
