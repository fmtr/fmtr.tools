import socket
from dataclasses import dataclass

from fmtr.tools.dns_tools.dm import Exchange
from fmtr.tools.logging_tools import logger


@dataclass
class Plain:
    """

    Base for starting a plain DNS server

    """

    host: str
    port: int

    def __post_init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def resolve(self, exchange: Exchange):
        raise NotImplemented

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
            self.resolve(exchange)
            sock.sendto(exchange.response.message.to_wire(), (ip, port))
