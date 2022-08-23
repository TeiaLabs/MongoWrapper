from __future__ import annotations

from ..base import BaseMixin
from ..utils import BaseConfig


class PartialMixin(BaseMixin):

    @classmethod
    def partial(cls):
        class Partial(cls):
            def __new__(cls, *_, **__):
                subclass_dict = cls.Config.__dict__
                fields_always_validated = subclass_dict.get("always_validate", set())

                base_config = {
                    k: getattr(BaseConfig, k)
                    for k in dir(BaseConfig)
                    if not k.startswith('__')
                }
                for key in base_config:
                    if key not in subclass_dict:
                        setattr(cls.Config, key, base_config[key])

                fields = cls.__dict__.get("__fields__", {})
                for field_name in fields:
                    if field_name not in fields_always_validated:
                        fields[field_name].required = False
                        fields[field_name].allow_none = True

                return super().__new__(cls)

        return Partial
