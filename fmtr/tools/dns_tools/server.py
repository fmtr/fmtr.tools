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
            exchange.response.is_complete = True

    def handle(self, exchange: Exchange):
        """

        Check validity of request, presence in cache and resolve.

        """
        request = exchange.request

        if not request.is_valid:
            raise ValueError(f'Only one question per request is supported. Got {len(request.question)} questions.')

        span = logger.span(
            f'Handling request {request.message.id=} {request.type_text} {request.name_text} {request.question=} {exchange.ip=} {exchange.port=}...'
        )
        with span:

            with logger.span(f'Checking cache...'):
                self.check_cache(exchange)

            if not exchange.response.is_complete:
                exchange = self.resolve(exchange)
                exchange.response.is_complete = True

            self.cache[exchange.key] = exchange.response
            logger.info(f'Resolution complete {request.message.id=} {exchange.response.rcode_text=} {exchange.response.answer=}')

            attribs = dict(rcode=exchange.response.rcode, rcode_text=exchange.response.rcode_text)
            span.set_attributes(attribs)

        return exchange
