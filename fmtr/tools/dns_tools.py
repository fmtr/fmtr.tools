import dns
import httpx
import socket
from dns.message import Message, QueryMessage


class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def resolve(self, message: Message) -> QueryMessage:
        raise NotImplemented

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"Listening on {self.host}:{self.port}")
        while True:
            data, addr = sock.recvfrom(512)
            question = dns.message.from_wire(data)
            answer = self.resolve(question)
            sock.sendto(answer.to_wire(), addr)


class Proxy(Server):
    url = "https://cloudflare-dns.com/dns-query"
    headers = {"accept": "application/dns-json"}

    def resolve(self, question: Message) -> Message:
        qname = question.question[0].name.to_text()
        qtype = dns.rdatatype.to_text(question.question[0].rdtype)
        params = {"name": qname, "type": qtype}

        response = httpx.get(self.url, headers=self.headers, params=params)
        response.raise_for_status()

        answer = dns.message.make_response(question)
        answer.flags |= dns.flags.RA

        data = response.json()
        for answer_rr in data.get("Answer", []):
            name = dns.name.from_text(answer_rr["name"])
            rtype = answer_rr["type"]
            ttl = answer_rr["TTL"]
            rdata = dns.rdata.from_text(dns.rdataclass.IN, rtype, answer_rr["data"])
            rrset = dns.rrset.from_rdata(name, ttl, rdata)
            answer.answer.append(rrset)

        return answer


if __name__ == "__main__":
    proxy = Proxy("127.0.0.1", 5354)
    proxy.start()
