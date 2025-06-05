import dns
import httpx
from dataclasses import dataclass
from dns.message import Message
from functools import cached_property
from typing import Self, Optional


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

    @cached_property
    def answer(self):
        return self.message.answer[-1]


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
