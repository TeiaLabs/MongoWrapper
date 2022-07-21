from .mixins import (
    BatchModelMixin,
    CountDocumentsMixin,
    ChildMixin,
    ModelMixin
)


class DocumentMixin(
    BatchModelMixin,
    CountDocumentsMixin,
    ChildMixin,
    ModelMixin
):
    pass
