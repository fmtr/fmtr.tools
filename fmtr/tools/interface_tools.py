from time import sleep
from typing import ClassVar

import streamlit as st

from fmtr.tools.data_modelling_tools import Base
from fmtr.tools.logging_tools import logger
from fmtr.tools.path_tools import Path


class Interface(Base):
    """

    Base for using streamlit via classes

    """

    PATH: ClassVar = __file__
    LAYOUT: ClassVar = 'centered'

    parent: Base = None
    st: ClassVar = st

    def set_title(self):
        """

        Set page title and layout when root interface

        """

        self.st.set_page_config(page_title=self.NAME, layout=self.LAYOUT)
        self.st.title(self.NAME)

    def render(self):
        """

        Render the Interface

        """
        raise NotImplementedError()

    def get_key(self, seg=None):
        """

        Get a structure-friendly unique ID

        """
        if self.parent is None:
            base = Path()
        else:
            base = self.parent.get_key() / str(id(self))

        if seg:
            path = base / seg
        else:
            path = base

        return path

    def to_tabs(self, *classes):
        """

        Add tabs from a list of interface classes

        """
        tab_names = [cls.NAME for cls in classes]
        tabs = st.tabs(tab_names)

        for cls, tab in zip(classes, tabs):
            with tab:
                cls()

    @classmethod
    def is_streamlit(cls):
        """

        Infer whether we are running within StreamLit

        """
        return bool(st.context.headers)

    @classmethod
    @st.cache_resource(show_spinner=False)
    def get_state(cls):
        """

        Initialise this Interface and keep cached

        """
        msg = f'Initialising State "{cls.NAME}"...'
        logger.info(msg)
        self = cls()
        return self

    @classmethod
    def launch(cls):
        """

        Launch StreamLit, if not already running - otherwise get self from cache and render

        """
        if cls.is_streamlit():
            self = cls.get_state()
            logger.debug(f'Rendering Interface "{self.NAME}" with state: {st.session_state}...')
            self.set_title()
            self.render()
        else:
            from streamlit.web import bootstrap
            bootstrap.run(cls.PATH, False, [], {})


class InterfaceTest(Interface):
    NAME: ClassVar = 'Test Interface'

    parent: Base = None

    def render(self):
        """

        Render the Interface

        """
        if not self.st.button('Run Test'):
            return
        msg = 'Running test...'
        with self.st.spinner(msg):
            sleep(3)
        self.st.success("Success!")


if __name__ == '__main__':
    InterfaceTest.launch()
