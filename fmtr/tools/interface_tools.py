from time import sleep

import streamlit as st

from fmtr.tools.logging_tools import logger


class Interface:
    """

    Base for using streamlit via classes

    """

    PATH = __file__
    LAYOUT = 'centered'
    NAME = 'Base Interface'

    st = st

    def __init__(self, is_root=False):
        """

        Set up page layout and call loop method

        """
        logger.debug(f'Running interface loop with state: {st.session_state}...')

        if is_root:
            self.set_title()

        self.loop()

    def set_title(self):
        """

        Set page title and layout when root interface

        """

        st.set_page_config(page_title=self.NAME, layout=self.LAYOUT)
        st.title(self.NAME)

    def loop(self):
        """

        Dummy process to simulate a task

        """

        if not st.button('Run Test'):
            return
        msg = 'Running test...'
        with st.spinner(msg):
            sleep(3)
        st.success("Success!")

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
    def launch(cls):
        """

        Launch StreamLit, if not already running - otherwise instantiate to run loop method

        """
        if cls.is_streamlit():
            cls(is_root=True)
        else:
            from streamlit.web import bootstrap
            bootstrap.run(cls.PATH, False, [], {})
