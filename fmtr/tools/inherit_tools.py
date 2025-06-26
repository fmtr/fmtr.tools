from typing import TypeVar, Generic

T = TypeVar("T")


class Inherit(Generic[T]):
    """

    Runtime inheritance. Acts like a wrapper around an instantiated base class of type T, and allows overriding methods in subclasses like regular inheritance.

    """

    def __init__(self, parent: T):
        """

        Set parent

        """
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, name):
        """

        Since regular attribute access checks own methods first, we don't need to do anything fancy to fall back to the parent when not implemented.

        """
        return getattr(self._parent, name)
