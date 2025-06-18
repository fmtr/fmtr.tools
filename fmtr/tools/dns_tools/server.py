import socket
from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property

from fmtr.tools import caching_tools as caching
from fmtr.tools.dns_tools.dm import Exchange
from fmtr.tools.logging_tools import logger


@dataclass(kw_only=True, eq=False)
class Plain:
    """

    Base for starting a plain DNS server

    """

    host: str
    port: int

    @cached_property
    def sock(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @cached_property
    def cache(self):
        """

        Overridable cache.

        """
        cache = caching.TLRU(maxsize=1_024, ttu_static=timedelta(hours=1), desc='DNS Request')
        return cache

    def start(self):
        """

        Listen and resolve via overridden resolve method.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        logger.info(f'Listening on {self.host}:{self.port}')
        while True:
            data, (ip, port) = sock.recvfrom(512)
            exchange = Exchange.from_wire(data, ip=ip, port=port)
            self.handle(exchange)
            sock.sendto(exchange.response.message.to_wire(), (ip, port))

    def resolve(self, exchange: Exchange) -> Exchange:
        """

        Defined in subclasses

        """
        raise NotImplemented

    def check_cache(self, exchange: Exchange):
        """

        Check cache, patch in in new ID and mark complete

        """
        if exchange.key in self.cache:
            logger.info(f'Request found in cache.')
            exchange.response = self.cache[exchange.key]
            exchange.response.message.id = exchange.request.message.id
            exchange.is_complete = True

    def get_span(self, exchange: Exchange):
        """

        Get handling span

        """
        request = exchange.request
        span = logger.span(
            f'Handling request {exchange.client_name=} {request.message.id=} {request.type_text} {request.name_text} {request.question=}...'
        )
        return span

    def log_response(self, exchange: Exchange):
        """

        Log when resolution complete

        """
        request = exchange.request
        response = exchange.response

        logger.info(
            f'Resolution complete {exchange.client_name=} {request.message.id=} {request.type_text} {request.name_text} {request.question=} {exchange.is_complete=} {response.rcode=} {response.rcode_text=} {response.answer=} {response.blocked_by=}...'
        )



    def handle(self, exchange: Exchange):
        """

        Check validity of request, reverse lookup client address, check presence in cache and resolve.

        """

        if not exchange.request.is_valid:
            raise ValueError(f'Only one question per request is supported. Got {len(exchange.request.question)} questions.')

        if not exchange.is_internal:
            self.handle(exchange.reverse)
            client_name = exchange.reverse.question_last.name.to_text()
            if not exchange.reverse.response.answer:
                logger.warning(f'Client name could not be resolved {client_name=}.')
            exchange.client_name = client_name

        with self.get_span(exchange):
            with logger.span(f'Checking cache...'):
                self.check_cache(exchange)

            if not exchange.is_complete:
                exchange = self.resolve(exchange)
                exchange.is_complete = True

            self.cache[exchange.key] = exchange.response
            self.log_response(exchange)

        return exchange
