import uvicorn
from dataclasses import dataclass
from fastapi import FastAPI, Request
from typing import Callable, List, Optional, Union

from fmtr.tools.environment_tools import IS_DEBUG
from fmtr.tools.iterator_tools import enlist
from fmtr.tools.logging_tools import logger


@dataclass
class Endpoint:
    """

    Endpoint-as-method config

    """
    method: Callable
    path: str
    tags: Optional[Union[str, List[str]]] = None
    method_http: Optional[Callable] = None

    def __post_init__(self):
        self.tags = enlist(self.tags)


class ApiBase:
    """

    Simple API base class, generalising endpoint-as-method config.

    """
    TITLE = 'Base API'
    HOST = '0.0.0.0'
    PORT = 8080

    def add_endpoint(self, endpoint: Endpoint):
        """

        Add endpoints from definitions using a single dataclass instance.

        """
        method_http = endpoint.method_http or self.app.post
        doc = (endpoint.method.__doc__ or '').strip() or None

        method_http(
            endpoint.path,
            tags=endpoint.tags,
            description=doc,
            summary=doc
        )(endpoint.method)

    def __init__(self):
        self.app = FastAPI(title=self.TITLE)

        for endpoint in self.get_endpoints():
            self.add_endpoint(endpoint)

        if IS_DEBUG:
            self.app.exception_handler(Exception)(self.handle_exception)

    def get_endpoints(self) -> List[Endpoint]:
        """

        Define endpoints using a dataclass instance.

        """
        endpoints = [

        ]

        return endpoints

    async def handle_exception(self, request: Request, exception: Exception):
        """

        Actually raise exceptions (e.g. for debugging) instead of returning a 500.

        """
        exception
        raise


    @classmethod
    def launch(cls):
        self = cls()
        logger.info(f'Launching API {cls.TITLE}...')
        uvicorn.run(self.app, host=self.HOST, port=self.PORT)


if __name__ == '__main__':
    ApiBase.launch()
