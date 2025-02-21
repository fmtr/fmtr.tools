from time import sleep
from typing import ClassVar

from fmtr.tools.data_modelling_tools import Base
from fmtr.tools.logging_tools import logger
from fmtr.tools.path_tools import Path


def material(name):
    """

    Get Material Design icon markdown

    """
    return f":material/{name}:"


def color(name, text):
    """

    Get markdown coloured text

    """
    return f":{name}[{text}]"


def get_streamlit():
    import streamlit
    return streamlit

class Interface(Base):
    """

    Base for using streamlit via classes

    """

    PATH: ClassVar = __file__
    LAYOUT: ClassVar = 'centered'
    NAME: ClassVar = None
    IS_ASYNC: ClassVar = False

    parent: Base = None

    @property
    def st(self):
        return get_streamlit()

    @classmethod
    def get_name(cls):
        return cls.NAME or cls.__name__

    def set_title(self):
        """

        Set page title and layout when root interface

        """

        self.st.set_page_config(page_title=self.get_name(), layout=self.LAYOUT)
        self.st.title(self.get_name())

    def render(self):
        """

        Render the Interface

        """
        raise NotImplementedError()

    def get_key(self, seg=None):
        """

        Get a structure-friendly unique ID

        """

        suffix = f'{self.__class__.__name__}({self.get_key_self()})'

        if self.parent is None:
            base = Path(suffix)
        else:
            base = self.parent.get_key() / suffix

        if seg:
            path = base / seg
        else:
            path = base

        return path

    def get_url_data(self):
        """

        Get URL params data pertaining to the current object

        """

        if self.parent is None:
            data = {}
        else:
            data = self.parent.get_url_data()

        url_self = self.get_url_self()

        if url_self:
            data |= {self.__class__.__name__.lower(): url_self}

        return data

    def get_url_self(self):
        """

        Get URL params ID pertaining to the current object

        """
        return str(id(self))

    def get_key_self(self):
        """

        Get a streamlit key pertaining to the current object

        """
        return str(id(self))

    def get_url(self):
        """

        Get URL string suffix pertaining to the current object

        """
        import urllib
        return urllib.parse.urlencode(self.get_url_data())

    def to_tabs(self, *classes):
        """

        Add tabs from a list of interface classes

        """
        tab_names = [cls.get_name() for cls in classes]
        tabs = st.tabs(tab_names)

        for cls, tab in zip(classes, tabs):
            with tab:
                cls()

    @classmethod
    def is_streamlit(cls):
        """

        Infer whether we are running within StreamLit

        """
        return bool(get_streamlit().context.headers)

    @classmethod
    def get_state(cls):
        """

        Initialise this Interface and keep cached. This needs to be a cached_resource to avoid serialisation/copying.
        This is global, so session handling needs to happen downstream.

        """
        msg = f'Initialising State "{cls.get_name()}"...'
        logger.info(msg)
        self = cls()
        return self

    @classmethod
    def launch(cls):
        """

        Launch StreamLit, if not already running - otherwise get self from cache and render

        """

        st = get_streamlit()

        if cls.is_streamlit():

            if cls.IS_ASYNC:
                from fmtr.tools import async_tools
                async_tools.ensure_loop()

            self = st.cache_resource(show_spinner=False)(cls.get_state)()
            logger.debug(f'Rendering Interface "{self.get_name()}" with state: {st.session_state}...')
            self.set_title()
            self.render()
        else:
            logger.info(f'Launching Streamlit interface "{cls.get_name()}"...')
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

