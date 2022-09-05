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
            dogs.append(
                await Dog.create(Dog(
                    name=f"Dog {i + j}", 
                    treats=random.sample(treats, k=random.randint(0, len(treats)))
                ))
            )

        await DogOwner.create(DogOwner(
            name=f"Ownerr {i}",
            dogs=dogs,
        ))

    out = await DogOwner.count("dogs.treats")[0]
    assert not set(out.keys()).difference(set("_id", "name", "dogs"))

    dogs = out["dogs"][0]
    assert not set(dogs.keys()).difference(set("_id", "name", "treats"))

    assert isinstance(dogs["treats"], int)