from functools import cached_property

import flet as ft
from flet.core.types import AppView
from flet.core.view import View

from fmtr.tools import environment_tools
from fmtr.tools.constants import Constants
from fmtr.tools.function_tools import MethodDecorator
from fmtr.tools.logging_tools import logger


class update(MethodDecorator):
    """

    Update the page after the decorated function is called.

    """

    def stop(self, instance):
        instance.page.update()


class progress(update):
    """

    Run the function while a progress indicator (e.g. spinner) is and within the object-defined context (e.g. logging span).

    """

    def get_context(self, instance):
        """

        Use instance-defined context.

        """
        return instance.context

    def start(self, instance):
        """

        Make progress visible and update.

        """
        instance.progress.visible = True
        instance.page.update()

    def stop(self, instance):
        """

         Make progress not visible and update.

        """
        instance.progress.visible = False
        super().stop(instance)




class Interface(ft.Column):
    """

    Simple interface base class.

    """
    TITLE = 'Base Interface'
    HOST = '0.0.0.0'
    PORT = 8080
    URL = Constants.FMTR_DEV_INTERFACE_URL if environment_tools.IS_DEV else None
    APPVIEW = AppView.WEB_BROWSER
    PATH_ASSETS = None
    ROUTE_ROOT = '/'
    SCROLL = ft.ScrollMode.AUTO

    def __init__(self, *args, **kwargs):
        """

        Instantiate and apply interface config

        """
        super().__init__(*args, **kwargs, scroll=self.SCROLL)

    @classmethod
    def render(cls, page: ft.Page):
        """

        Interface entry point. Set relevant callbacks, and add instantiated self to page views

        """
        if not page.on_route_change:
            page.theme = cls.get_theme()
            page.views.clear()
            self = cls()
            view = self.view
            if not view:
                view = self
            page.views.append(view)
            page.on_route_change = cls.route
            page.on_view_pop = cls.pop

            page.go(cls.ROUTE_ROOT)

    @cached_property
    def view(self):
        """

        Overridable view definition.

        """
        return None

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

    @classmethod
    def get_theme(self):
        """

        Overridable theme definition

        """
        text_style = ft.TextStyle(size=20)
        theme = ft.Theme(
            text_theme=ft.TextTheme(body_large=text_style),
        )
        return theme

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
