import inspect

import flet as ft


class ContextBase:
    """

    A mixin base that can be used as both a synchronous and asynchronous context manager,
    or as a decorator to wrap synchronous or asynchronous functions.
    The control becomes visible when entering the context or invoking the wrapped function,
    and is hidden again when exiting.

    """

    def start(self):
        """

        Show the control and update the page.
        """

        self.visible = True
        self.page.update()

    def stop(self):
        """

        Hide the control and update the page.
        
        """
        self.visible = False
        self.page.update()

    def context(self, func):
        """

        Decorator that wraps a synchronous or asynchronous function.
        While the function runs, the control is visible.

        """
        if inspect.iscoroutinefunction(func):
            async def async_wrapped(*args, **kwargs):
                async with self:
                    return await func(*args, **kwargs)

            return async_wrapped
        else:
            def sync_wrapped(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)

            return sync_wrapped

    def __enter__(self):
        """

        Enter the control context (sync).

        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        Exit the control context (sync).

        """
        self.stop()

    async def __aenter__(self):
        """

        Enter the control context (async).
        """

        result = self.start()
        if inspect.isawaitable(result):
            await result
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """

        Exit the control context (async).
        """

        result = self.stop()
        if inspect.isawaitable(result):
            await result


class ContextRing(ft.ProgressRing, ContextBase):
    """

    A progress ring as a context manager.

    """

    def __init__(self, *args, **kwargs):
        """

        Initialize the progress ring as hidden by default.

        """
        super().__init__(*args, **kwargs, visible=False)

class ProgressButton(ft.Button):
    """

    Button containing a progress ring.

    """

    def __init__(self, *args, on_click=None, ring: ContextRing = None, **kwargs):
        """

        Run on_click in run context manager

        """
        self.ring = ring or ContextRing()

        super().__init__(*args, content=self.ring, on_click=self.ring.context(on_click), **kwargs)
        self.context = self.ring.context


class SliderSteps(ft.Slider):
    """

    Slider control using step instead of divisions

    """

    def __init__(self, *args, min=10, max=100, step=10, **kwargs):
        self.step = step
        divisions = (max - min) // step
        super().__init__(*args, min=min, max=max, divisions=divisions, **kwargs)
