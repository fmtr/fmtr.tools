from flet.core.page import Page

from fmtr.tools.data_modelling_tools import Base, MixinArbitraryTypes


class Context(Base, MixinArbitraryTypes):
    """

    Base context class

    """
    page: Page
