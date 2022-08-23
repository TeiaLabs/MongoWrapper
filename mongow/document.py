from .mixins import *


class DocumentMixin(
    AggregateMixin,
    BatchCreateMixin,
    BatchUpdateMixin,
    CountMixin,
    CreateMixin,
    DeleteMixin,
    IndexMixin,
    PartialMixin,
    UpdateMixin,
    UpsertMixin
):
    pass
