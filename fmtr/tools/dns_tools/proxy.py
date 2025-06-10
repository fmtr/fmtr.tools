from dataclasses import dataclass

from fmtr.tools import logger
from fmtr.tools.dns_tools import server, client
from fmtr.tools.dns_tools.dm import Exchange


@dataclass
class Proxy(server.Plain):
    """

    Base for a DNS Proxy server (plain server) TODO: Allow subclassing of any server type.

    """

    client: client.HTTP

    def process_question(self, exchange: Exchange):
        """

        Modify exchange based on initial question.

        """
        return

    def process_upstream(self, exchange: Exchange):
        """

        Modify exchange after upstream response.

        """
        return

    def resolve(self, exchange: Exchange):
        """

        Resolve a request, processing each stage, initial question, upstream response etc.
        Subclasses can override the relevant processing methods to implement custom behaviour.

        """

        request = exchange.request

        with logger.span(f'Handling request {request.message.id=} {request.question=} {exchange.client=}...'):

            if not request.is_valid:
                raise ValueError(f'Only one question per request is supported. Got {len(request.question)} questions.')

            with logger.span(f'Processing question...'):
                self.process_question(exchange)
            if exchange.response.is_complete:
                return

            with logger.span(f'Making upstream request...'):
                self.client.resolve(exchange)
            if exchange.response.is_complete:
                return

            with logger.span(f'Processing upstream response...'):
                self.process_upstream(exchange)
            if exchange.response.is_complete:
                return

            exchange.response.is_complete = True

        logger.info(f'Resolution complete {request.message.id=} {exchange.response.answer=}')
        return
