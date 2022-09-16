import pytest

from tests.schemas import DogOwner, Dog


class TestCounting:
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

    @pytest.fixture(autouse=True)
    async def create_entities(self):
        dog_owners = []
        for i in range(10):
            dogs = [
                Dog(
                    name=f"Dog {i} {j}",
                    treats=self.treats[:j]
                )
                for j in range(i)
            ]
            dog_owners.append(
                DogOwner(
                    name=f"Owner {i}",
                    dogs=dogs,
                ) 
            )
        oids = await DogOwner.create_many(dog_owners)
        yield
        await DogOwner.delete({"_id": {"$in": oids}})

    async def test_count_nested_1_level(self):
        output = await DogOwner.count_nested("dogs")
        for doc in output:
            assert doc["dogs"] == int(doc["name"][-1])

    async def test_count_nested_2_levels(self):
        output = await DogOwner.count_nested("dogs.treats")
        # out = output[0]
        # assert not set(out.keys()).difference({"_id", "name", "dogs"})
        # dogs = out["dogs"]
        # assert not set(dogs.keys()).difference({"_id", "name", "treats"})
        # assert isinstance(dogs["treats"], int)
        for doc in output:
            for sub_doc in doc["dogs"]:
                assert sub_doc["treats"] == sub_doc["name"].split(" ")[-1]
    
    async def test_count(self):
        output = await DogOwner.count()
        assert output == 10