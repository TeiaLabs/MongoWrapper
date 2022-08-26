import random

from tests.schemas import Fruit


async def test_read_offset():
    for i in range(100):
        await Fruit.create(
            data=Fruit(
                density=random.random(),
                name=f"Fruit {i}",
                taste="sweet",
            )
        )
    out = await Fruit.read(offset=97, limit=3)
    assert len(out) == 3
