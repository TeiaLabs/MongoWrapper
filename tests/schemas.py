import random
from typing import Literal

import mongow
import pydantic


class Fruit(mongow.BaseMixin):
    density: float = 1.0
    name: str
    needs_peeling: bool = pydantic.Field(
        default=True, alias="needsPeeling"
    )
    taste: Literal["bitter", "sweet"]

    __collection__ = "fruits"


class Dog(mongow.BaseMixin):
    name: str
    age: int = random.randint(0, 20)
    treats: list[str]

    __collection__ = "dogs"


class DogOwner(mongow.BaseMixin):
    name: str
    age: int = random.randint(0, 100)
    dogs: list[Dog]

    __collection__ = "dog_owners"


class NGO(mongow.BaseMixin):
    name: str
    funding: int = random.randint(0, 1000000)
    dog_owners: list[DogOwner]

    __collection__ = "ngos"


