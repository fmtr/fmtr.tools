import inspect
from functools import cached_property
from typing import ClassVar, List, Any, Dict

from pydantic import BaseModel
from pydantic import RootModel, ConfigDict
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined, PydanticUndefinedType

from fmtr.tools.datatype_tools import is_optional
from fmtr.tools.iterator_tools import get_class_lookup
from fmtr.tools.string_tools import camel_to_snake
from fmtr.tools.tools import Auto, Required, Empty


class Field(FieldInfo):
    """

    Allow DRYer field definitions, set annotation and defaults at the same time, easier field inheritance, etc.

    """
    NAME = Auto
    ANNOTATION = Empty
    EXCLUDE = False
    DEFAULT = Auto
    FILLS = None
    DESCRIPTION = None
    TITLE = Auto
    CONFIG = None

    def __init__(self, annotation=Empty, default=Empty, description=None, title=None, fills=None, exclude=None, **kwargs):
        """

        Infer default from type annotation, if enabled, use class/argument fills to create titles/descriptions, etc.

        """

        fills_super = getattr(super(), 'FILLS', None)
        self.fills = (fills_super or {}) | (self.FILLS or {}) | (fills or {})

        exclude = exclude if exclude is not None else self.EXCLUDE

        self.annotation = self.ANNOTATION if annotation is Empty else annotation
        if self.annotation is Empty:
            raise ValueError("Annotation must be specified.")
        annotation = self.annotation

        default = self.get_default_auto(default)
        if default is Required:
            default = PydanticUndefined

        description = self.get_desc(description)
        title = self.get_title_auto(title)
        kwargs |= (self.CONFIG or {})

        super().__init__(default=default, title=title, description=description, exclude=exclude, **kwargs)
        self.annotation = annotation

    @classmethod
    def get_name_auto(cls) -> str:
        """

        Infer field name, if set to auto.

        """
        if cls.NAME is Auto:
            return camel_to_snake(cls.__name__)
        elif cls.NAME is None:
            return cls.__name__

        return cls.NAME

    @cached_property
    def fills(self) -> Dict[str, str]:
        """

        Get fills with filled title merged in

        """

        fills_super = getattr(super(), 'FILLS', None)

        return (fills_super or {}) | (self.FILLS or {}) | dict(title=self.get_title_auto())

    def get_default_auto(self, default) -> type[Any] | None | PydanticUndefinedType:
        """

        Infer default, if not specified.

        """

        if default is not Empty:
            return default

        if self.DEFAULT is not Auto:
            return self.DEFAULT

        if is_optional(self.annotation):
            return None
        else:
            return Required

    def get_title_auto(self, mask) -> str | None:
        """

        Get title from classname/mask

        """

        if not mask:
            mask = self.__class__.__name__ if self.TITLE is Auto else self.TITLE

        if mask:
            return mask.format(**self.fills)

        return None

    def get_desc(self, mask) -> str | None:
        """

        Fill description mask, if specified

        """

        mask = mask or self.DESCRIPTION

        if mask:
            return mask.format(**self.fills)

        return None


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

    Base model allowing model definition via a list of custom Field objects.

    """
    FIELDS: ClassVar[List[Field] | Dict[str, Field]] = []

    def __init_subclass__(cls, **kwargs):
        """

        Fetch aggregated fields metadata from the hierarchy and set annotations and FieldInfo objects in the class.

        """
        super().__init_subclass__(**kwargs)

        fields = {}
        for base in reversed(cls.__mro__):

            try:
                raw = base.FIELDS
            except AttributeError:
                raw = {}

            if isinstance(raw, dict):
                fields |= raw
            else:
                fields |= get_class_lookup(*raw, name_function=lambda cls_field: cls_field.get_name_auto())

        cls.FIELDS = fields

        for name, field in fields.items():
            if name in cls.__annotations__:
                continue

            if inspect.isclass(field):
                field = field()

            setattr(cls, name, field)
            cls.__annotations__[name] = field.annotation

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
