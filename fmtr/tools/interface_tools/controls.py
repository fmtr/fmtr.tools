import flet as ft


class ContextRing(ft.ProgressRing):
    """

    Context manager progress ring.

    """

    def __init__(self, *args, **kwargs):
        """

        Start out not visible.

        """
        super().__init__(*args, **kwargs, visible=False)

    def start(self):
        """

        Update to visible when in context.

        """
        self.visible = True
        self.page.update()

    def stop(self):
        """

        Update to not visible when exiting context.

        """
        self.visible = False
        self.page.update()

    def context(self, func):
        """

        Context manager decorator.

        """

        def wrapped(*args, **kwargs):
            with self:
                func(*args, **kwargs)

        return wrapped

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class ProgressButton(ft.Button):
    """

    Button with progress ring.

    """

    def __init__(self, *args, on_click=None, **kwargs):
        """

        Run on_click in run context manager

        """
        self.ring = ContextRing()
        super().__init__(*args, content=self.ring, on_click=self.ring.context(on_click), **kwargs)
        self.context = self.ring.context
