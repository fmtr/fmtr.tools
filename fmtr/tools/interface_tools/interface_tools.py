import flet as ft
from flet.core.types import AppView
from flet.core.view import View

from fmtr.tools.logging_tools import logger


def update(func):
    """

    Page update decorator

    """

    def wrapped(*args, **kwargs):
        func(*args, **kwargs)
        func.__self__.page.update()

    return wrapped

class Interface(ft.Column):
    """

    Simple interface base class.

    """
    TITLE = 'Base Interface'
    HOST = '0.0.0.0'
    PORT = 8080
    URL = None
    APPVIEW = AppView.WEB_BROWSER
    PATH_ASSETS = None
    ROUTE_ROOT = '/'

    THEME = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.PINK))

    @classmethod
    def render(cls, page: ft.Page):
        """

        Interface entry point. Set relevant callbacks, and add instantiated self to page views

        """
        if not page.on_route_change:
            page.theme = cls.THEME
            page.views.clear()
            page.views.append(cls())

            page.on_route_change = cls.route
            page.on_view_pop = cls.pop

            page.go(cls.ROUTE_ROOT)

    @classmethod
    def route(cls, event: ft.RouteChangeEvent):
        """

        Overridable router.

        """
        logger.debug(f'Route change: {event=}')

    @classmethod
    def pop(cls, view: View, page: ft.Page):
        """

        Overridable view pop.

        """
        logger.debug(f'View popped: {page.route=} {len(page.views)=} {view=}')

    @classmethod
    def launch(cls):
        """

        Launch via render method

        """

        if cls.URL:
            url = cls.URL
        else:
            url = f'http://{cls.HOST}:{cls.PORT}'

        logger.info(f"Launching {cls.TITLE} at {url}")
        ft.app(cls.render, view=cls.APPVIEW, host=cls.HOST, port=cls.PORT, assets_dir=cls.PATH_ASSETS)


class Test(Interface):
    """

    Simple test interface.

    """
    TITLE = 'Test Interface'

    def __init__(self):
        controls = [ft.Text(self.TITLE)]
        super().__init__(controls=controls)

if __name__ == "__main__":
    Test.launch()
