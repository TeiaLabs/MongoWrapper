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
