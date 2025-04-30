from pydantic import BaseModel, RootModel, ConfigDict


def to_df(*objs, name_value='value'):
    """

    DataFrame representation of Data Models as rows.

    """
    from fmtr.tools import tabular

    rows = []
    for obj in objs:
        if isinstance(obj, BaseModel):
            row = obj.model_dump()
        else:
            row = {name_value: obj}
        rows.append(row)

    df = tabular.DataFrame(rows)
    if 'id' in df.columns:
        df.set_index('id', inplace=True, drop=True)
    return df


class MixinArbitraryTypes:
    """

    Convenience for when non-serializable types are needed
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    def to_df(self, name_value='value'):
        """

        DataFrame representation with Fields as rows.

        """

        objs = []
        for name in self.model_fields.keys():
            val = getattr(self, name)
            objs.append(val)

        df = to_df(*objs, name_value=name_value)
        df['id'] = list(self.model_fields.keys())
        df = df.set_index('id', drop=True)
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
