from .mixins import *


class DocumentMixin(
    AggregateMixin,
    BatchCreateMixin,
    BatchUpdateMixin,
    CountMixin,
    CreateMixin,
    DeleteMixin,
    IndexMixin,
    UpdateMixin,
    UpsertMixin
):
    pass
