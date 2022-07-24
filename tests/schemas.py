from typing import Literal

import pydantic

import mongow

class Fruit(mongow.DocumentMixin):
    density: float = 1.0
    name: str
    needs_peeling: bool = pydantic.Field(
        default=True, alias="needsPeeling"
    )
    taste: Literal["bitter", "sweet"]

    __collection__ = "fruits"
