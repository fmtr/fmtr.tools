import beanie
from functools import cached_property
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from fmtr.tools.constants import Constants


class Document(beanie.Document):
    """

    Document stub.

    """


class Client:

    def __init__(self, name, host=Constants.FMTR_DEV_HOST, port=27017, documents: List[beanie.Document] | None = None):
        self.name = name
        self.host = host
        self.port = port
        self.documents = documents

        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.name]

    @cached_property
    def uri(self):
        return f'mongodb://{self.host}:{self.port}'

    async def connect(self):
        return await beanie.init_beanie(database=self.db, document_models=self.documents)
