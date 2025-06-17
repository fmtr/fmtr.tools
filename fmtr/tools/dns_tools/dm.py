import dns
import httpx
from dataclasses import dataclass
from dns import rcode as dnsrcode
from dns.message import Message, QueryMessage
from dns.rrset import RRset
from functools import cached_property
from typing import Self, Optional

from fmtr.tools.string_tools import join


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
    is_complete: bool = False

    @classmethod
    def from_http(cls, response: httpx.Response) -> Self:
        """

        Initialise from an HTTP response.

        """
        self = cls(response.content, http=response)
        return self

    @property
    def answer(self) -> Optional[RRset]:
        """

        Get the latest answer, if one exists.

        """
        if not self.message.answer:
            return None
        return self.message.answer[-1]

    @property
    def rcode(self) -> dnsrcode.Rcode:
        return self.message.rcode()

    @property
    def rcode_text(self) -> str:
        return dnsrcode.to_text(self.rcode)

    def __str__(self):
        """

        Put answer and ID text in string representation.

        """
        answer = self.answer

        if answer:
            answer = join(answer.to_text().splitlines(), sep=', ')

        string = join([answer, self.message.flags], sep=', ')
        string = f'{self.__class__.__name__}({string})'
        return string



@dataclass
class Request(BaseDNSData):
    """

    DNS request object.

    """
    wire: bytes

    @cached_property
    def question(self) -> RRset:
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

    def get_response_template(self):
        message = dns.message.make_response(self.message)
        message.flags |= dns.flags.RA
        return message

    @cached_property
    def blackhole(self) -> Response:
        blackhole = self.get_response_template()
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


    @classmethod
    def from_wire(cls, wire: bytes, ip: str, port: int) -> Self:
        request = Request(wire)
        response = Response.from_message(request.get_response_template())

        return cls(request=request, response=response, ip=ip, port=port)

    @cached_property
    def client(self):
        return f'{self.ip}:{self.port}'

    @property
    def question_last(self) -> RRset:
        """

        Contrive an RRset representing the latest/current question. This can be the original question - or a hybrid one if we've injected our own answers into the exchange.

        """
        if self.response.answer:
            rrset = self.response.answer
            ty = self.request.type
            ttl = self.request.question.ttl
            rdclass = self.request.question.rdclass
            name = next(iter(rrset.items.keys())).to_text()

            rrset_contrived = dns.rrset.from_text(
                name=name,
                ttl=ttl,
                rdtype=ty,
                rdclass=rdclass,

            )

            return rrset_contrived
        else:
            return self.request.question  # Solves the issue of digging out the name.

    @property
    def query_last(self) -> QueryMessage:
        """

        Create a query (e.g. for use by upstream) based on the last question.

        """

        question_last = self.question_last
        query = dns.message.make_query(qname=question_last.name, rdclass=question_last.rdclass, rdtype=question_last.rdtype)
        return query

    @property
    def key(self):
        """

        Hashable key for caching

        """
        data = tuple(self.request.question.to_text().split())
        return data
