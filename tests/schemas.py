from typing import Literal

import mongow


class Fruit(mongow.BaseMixin):
    name: str
    taste: Literal["bitter", "sweet"]
    needs_peeling: bool = True
