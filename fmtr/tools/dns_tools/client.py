import dns
from dataclasses import dataclass
from dns import query
from functools import cached_property
from httpx_retries import Retry, RetryTransport

from fmtr.tools import http_tools as http
from fmtr.tools.dns_tools.dm import Exchange, Response, Request
from fmtr.tools.logging_tools import logger

RETRY_STRATEGY = Retry(
    total=2,  # initial + 1 retry
    allowed_methods={"GET", "POST"},
    status_forcelist={502, 503, 504},
    retry_on_exceptions=None,  # defaults to httpx.TransportError etc.
    backoff_factor=0.25,  # short backoff (e.g. 0.25s, 0.5s)
    max_backoff_wait=0.75,  # max total delay before giving up
    backoff_jitter=0.1,  # small jitter to avoid retry bursts
    respect_retry_after_header=False,  # DoH resolvers probably won't set this
)


class HTTPClientDoH(http.Client):
    """

    Base HTTP client for DoH-appropriate retry strategy.

    """
    TRANSPORT = RetryTransport(retry=RETRY_STRATEGY)


class ClientBasePlain:
    def __init__(self, host, port=53):
        self.host = host
        self.port = port

    def resolve(self, exchange: Exchange):
        with logger.span(f'UDP {self.host}:{self.port}'):
            response = query.udp(q=exchange.request.message, where=self.host, port=self.port)
            exchange.response_upstream = Response.from_message(response)


@dataclass
class ClientDoH:
    """

    Base DoH client.

    """

    HEADERS = {"Content-Type": "application/dns-message"}
    CLIENT = HTTPClientDoH()
    BOOTSTRAP = ClientBasePlain('8.8.8.8')

    host: str
    url: str


    @cached_property
    def ip(self):
        message = dns.message.make_query(self.host, dns.rdatatype.A, flags=0)
        request = Request.from_message(message)
        exchange = Exchange(request=request, ip=None, port=None)
        self.BOOTSTRAP.resolve(exchange)
        ip = next(iter(exchange.response_upstream.answer.items.keys())).address
        return ip

    def resolve(self, exchange: Exchange):
        """

        Resolve via DoH

        """
        request = exchange.request
        headers = self.HEADERS | dict(Host=self.host)
        url = self.url.format(host=self.ip)
        response_doh = self.CLIENT.post(url, headers=headers, content=request.wire)
        response_doh.raise_for_status()
        response = Response.from_http(response_doh)
        exchange.response_upstream = response
