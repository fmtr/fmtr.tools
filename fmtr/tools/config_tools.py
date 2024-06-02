"""

Config tools for downstream projects

"""
from dataclasses import dataclass, fields, Field as DataclassField

from typing import List, Type


class ConfigClass:
    """

    Base class for all config classes.

    """

    @classmethod
    def process_field(cls, field):
        """

        Post-process field

        """

    @classmethod
    def process_fields(cls):
        """

        Post-process fields

        """
        for field in cls.get_fields():
            cls.process_field(field)

    @classmethod
    def get_fields(cls) -> List[DataclassField]:
        """

        Return fields

        """
        return fields(cls)

    def __init_subclass__(cls, **kwargs):
        """

        Decorate subclasses as dataclasses

        """
        return dataclass(cls)


Field = Type
