import socket

from fmtr.tools import logger
from fmtr.tools.dns_tools.client import ClientDoH
from fmtr.tools.dns_tools.dm import Exchange, Response


class ServerBasePlain:
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


class ServerBaseDoHProxy(ServerBasePlain):
    """

    Base for a DNS Proxy server

    """

    def __init__(self, host, port, client: ClientDoH):
        super().__init__(host, port)
        self.client = client

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
                self.client.resolve(exchange)

            with logger.span(f'Processing upstream response...'):
                self.process_upstream(exchange)

            if exchange.response:
                return

            exchange.response = exchange.response_upstream
            return
