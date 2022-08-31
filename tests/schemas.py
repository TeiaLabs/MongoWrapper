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
    treats: list[str]

    __collection__ = "dogs"


class DogOwner(mongow.BaseMixin):
    name: str
    dogs: list[Dog]

    __collection__ = "dog_owners"
