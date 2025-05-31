import httpx
from httpx_retries import RetryTransport

from fmtr.tools import logging_tools

logging_tools.logger.instrument_httpx()


class Client(httpx.Client):
    """

    Instrumented client base

    """

    TRANSPORT = RetryTransport()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, transport=self.TRANSPORT, **kwargs)


client = Client()

if __name__ == '__main__':
    resp = client.get('http://httpbin.org/delay/10')
    resp
