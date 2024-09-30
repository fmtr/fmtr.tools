from pydantic import BaseModel, RootModel


class MixinFromJson:

    @classmethod
    def from_json(cls, json_str):
        """

        Error-tolerant deserialization

        """
        from fmtr.tools import json_fix
        data = json_fix.from_json(json_str, default={})

        if type(data) is dict:
            self = cls(**data)
        else:
            self = cls(data)

        return self


class Base(BaseModel, MixinFromJson):
    """

    Base model

    """
    ...


class Root(RootModel, MixinFromJson):
    """

    Root (list) model

    """
    ...
