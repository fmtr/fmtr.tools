import dns
import httpx
import socket
from dataclasses import dataclass
from dns.message import Message
from functools import cached_property
from httpx_retries import Retry, RetryTransport
from typing import Optional, Self

from fmtr.tools import Client, logger

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


class HTTPClientDoH(Client):
    """

    Base HTTP client for DoH-appropriate retry strategy.

    """
    TRANSPORT = RetryTransport(retry=RETRY_STRATEGY)


@dataclass
class BaseDNSData:
    """

    DNS response object.

    """
    wire: bytes

    @cached_property
    def message(self) -> Message:
        return dns.message.from_wire(self.wire)

    @classmethod
    def from_message(cls, message: Message) -> Self:
        return cls(message.to_wire())


@dataclass
class Response(BaseDNSData):
    """

    DNS response object.

    """

    http: Optional[httpx.Response] = None

    @classmethod
    def from_http(cls, response: httpx.Response) -> Self:
        self = cls(response.content, http=response)
        return self


@dataclass
class Request(BaseDNSData):
    """

    DNS request object.

    """
    wire: bytes

    @cached_property
    def question(self):
        return self.message.question[0]

    @cached_property
    def is_valid(self):
        return len(self.message.question) != 0

    @cached_property
    def type(self):
        return self.question.rdtype

    @cached_property
    def type_text(self):
        return dns.rdatatype.to_text(self.type)

    @cached_property
    def name(self):
        return self.question.name

    @cached_property
    def name_text(self):
        return self.name.to_text()

    @cached_property
    def blackhole(self) -> Response:
        blackhole = dns.message.make_response(self.message)
        blackhole.flags |= dns.flags.RA
        blackhole.set_rcode(dns.rcode.NXDOMAIN)
        response = Response.from_message(blackhole)
        return response


@dataclass
class Exchange:
    """

    Entire DNS exchange for a DNS Proxy: request -> upstream response -> response

    """
    ip: str
    port: int

    request: Request
    response: Optional[Response] = None
    response_upstream: Optional[Response] = None

    @classmethod
    def from_wire(cls, wire: bytes, ip: str, port: int) -> Self:
        request = Request(wire)
        return cls(request=request, ip=ip, port=port)

    @cached_property
    def client(self):
        return f'{self.ip}:{self.port}'


class BasePlain:
    """

    Base for starting a plain DNS server

    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def resolve(self, exchange: Exchange):
        raise NotImplemented

    def start(self):
        """

        Listen and resolve via overridden resolve method.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"Listening on {self.host}:{self.port}")
        while True:
            data, (ip, port) = sock.recvfrom(512)
            exchange = Exchange.from_wire(data, ip=ip, port=port)
            self.resolve(exchange)
            sock.sendto(exchange.response.wire, (ip, port))


class BaseDoHProxy(BasePlain):
    """

    Base for a DNS Proxy server

    """

    URL = None
    HEADERS = {"Content-Type": "application/dns-message"}
    client = HTTPClientDoH()

    def process_question(self, exchange: Exchange):
        return

    def process_upstream(self, exchange: Exchange):
        return

    def from_upstream(self, exchange: Exchange) -> Exchange:

        request = exchange.request
        response_doh = self.client.post(self.URL, headers=self.HEADERS, content=request.wire)
        response_doh.raise_for_status()
        response = Response.from_http(response_doh)
        exchange.response_upstream = response

        return exchange

    def resolve(self, exchange: Exchange):
        """

        Resolve a request, processing each stage, initial question, upstream response etc.
        Subclasses can override the relevant processing methods to implement custom behaviour.

        """

        request = exchange.request

        with logger.span(f'Handling request for {request.name_text} from {exchange.client}...'):

            if not request.is_valid:
                raise ValueError(f'Only one question per request is supported. Got {len(request.question)} questions.')

            with logger.span(f'Processing question...'):
                self.process_question(exchange)
            if exchange.response:
                return

            with logger.span(f'Making upstream request for {request.name_text}...'):
                self.from_upstream(exchange)

            with logger.span(f'Processing upstream response...'):
                self.process_upstream(exchange)

            if exchange.response:
                return

            exchange.response = exchange.response_upstream
            return
