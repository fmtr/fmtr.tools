import flet as ft
from flet.core.event import Event
from flet.core.types import AppView
from flet.core.view import View

from fmtr.tools.logging_tools import logger


class Interface:
    """

    Simple interface base class.

    """
    TITLE = 'Base Interface'
    HOST = '0.0.0.0'
    PORT = 8080
    APPVIEW = AppView.WEB_BROWSER
    PATH_ASSETS = None
    ROUTE_ROOT = '/'

    def render(self, page: ft.Page):
        """

        Interface entry point.

        """

        if not page.on_route_change:
            page.on_route_change = lambda e, page=page: self.route(page, e)
            page.on_view_pop = lambda view, page=page: self.pop(page, view)

            page.go(self.ROUTE_ROOT)

    def route(self, page: ft.Page, event: Event):
        """

        Overridable router.

        """
        raise NotImplementedError

    def pop(self, page: ft.Page, view: View):
        """

        Overridable view pop.

        """
        raise NotImplementedError

    @classmethod
    def launch(cls):
        """

        Initialise self and launch.

        """
        self = cls()
        logger.info(f"Launching {self.TITLE} at http://{self.HOST}:{self.PORT}")
        ft.app(self.render, view=self.APPVIEW, host=self.HOST, port=self.PORT, assets_dir=self.PATH_ASSETS)


if __name__ == "__main__":
    Interface.launch()
