import random

from tests.schemas import DogOwner, Dog


async def test_count():
    treats = [
        "Ziwi",
        "Stewart Pro",
        "BondVet",
        "Best Bully",
        "Charlee Bear",
        "Barkworthies",
        "Jiminy's",
        "ElleVet",
        "Greenies"
    ]
    for i in range(10):
        dogs = []
        for j in range(random.randint(1, 5)):
            dogs.append(Dog(
                name=f"Dog {i + j}",
                treats=random.sample(treats, k=random.randint(0, len(treats)))
            ))

            await Dog.create(dogs[-1])

        await DogOwner.create(DogOwner(
            name=f"Owner {i}",
            dogs=dogs,
        ))

    out = (await DogOwner.count("dogs.treats"))[0]
    assert not set(out.keys()).difference({"_id", "name", "dogs"})

    dogs = out["dogs"]
    assert not set(dogs.keys()).difference({"_id", "name", "treats"})

    assert isinstance(dogs["treats"], int)
