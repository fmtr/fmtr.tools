import functools
import inspect
from typing import Tuple

from fmtr.tools import context_tools


def combine_args_kwargs(args: dict=None, kwargs: dict=None) -> dict:
    """

    Combines arguments and keyword arguments into a single dictionary.

    """
    args = args or []
    kwargs = kwargs or {}
    args = {i: arg for i, arg in enumerate(args)}
    args.update(kwargs)
    if all(isinstance(key, int) for key in args.keys()):
        args = list(args.values())
    return args


def split_args_kwargs(args_kwargs: dict) -> Tuple[list, dict]:
    """

    Splits arguments and keyword arguments into a list and a dictionary.

    """
    if isinstance(args_kwargs, list):
        args, kwargs = args_kwargs, {}
    else:
        args = [arg for key, arg in args_kwargs.items() if isinstance(key, int)]
        kwargs = {key: arg for key, arg in args_kwargs.items() if not isinstance(key, int)}

    return args, kwargs


class BoundDecorator:
    """

    Bound method decorator with overridable start/stop and context manager

    """

    def __init__(self, func):
        self.func = func
        self.context_null = context_tools.null()
        functools.update_wrapper(self, func)

    def get_context(self, instance):
        """

        By default use a null context.

        """
        return self.context_null

    def __get__(self, instance, owner):
        """

        Wrap at runtime, call start/stop within context.

        """
        if instance is None:
            return self.func

        if inspect.iscoroutinefunction(self.func):
            async def async_wrapper(*args, **kwargs):
                with self.get_context(instance):
                    self.start(instance)
                    result = await self.func(instance, *args, **kwargs)
                    self.stop(instance)
                    return result

            return functools.update_wrapper(async_wrapper, self.func)

        else:
            def sync_wrapper(*args, **kwargs):
                with self.get_context(instance):
                    self.start(instance)
                    result = self.func(instance, *args, **kwargs)
                    self.stop(instance)
                    return result

            return functools.update_wrapper(sync_wrapper, self.func)

    def start(self, instance):
        pass

    def stop(self, instance):
        pass
