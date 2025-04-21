from pydantic import BaseModel, RootModel


def to_df(*objs):
    """

    DataFrame representation of Data Models as rows.

    """
    from fmtr.tools import tabular
    rows = [obj.model_dump() for obj in objs]
    df = tabular.DataFrame(rows)
    return df


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

    def to_df(self):
        """

        DataFrame representation with Fields as rows.

        """

        objs = []
        for name in self.model_fields.keys():
            val = getattr(self, name)
            objs.append(val)

        df = to_df(*objs)
        df['id'] = list(self.model_fields.keys())
        return df


class Root(RootModel, MixinFromJson):
    """

    Root (list) model

    """

    def to_df(self):
        """

        DataFrame representation with items as rows.

        """

        return to_df(*self.items)
