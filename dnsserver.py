#reference: https://gist.github.com/pklaus/b5a7876d4d2cf7271873


import datetime
import socketserver
import sys
import threading
import traceback

from dnslib import *


class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)


# D = DomainName('p5-dns.5700.network')
D = DomainName('cukak.')

IP = '50.116.41.109'
TTL = 60 * 5

records = {
    D: [A(IP), AAAA((0,) * 16), MX(D.mail)],
}


def dns_response(data):
    request = DNSRecord.parse(data)

    #print('dns response request', request)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]

    print('\n\n qn, D: \n\n', qn, D)
    if qn == D or qn.endswith('.' + D):

        for name, rrs in records.items():
            if name == qn:
                for rdata in rrs:
                    rqt = rdata.__class__.__name__
                    if qt in ['*', rqt]:
                        reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=TTL, rdata=rdata))
    print("---- Reply:\n", reply)

    return reply.pack()


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0],
                                               self.client_address[1]))
        try:
            data = self.get_data()
            print(len(data), data)  # repr(data).replace('\\x', '')[1:-1]
            self.send_data(dns_response(data))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


class DNSServer:
    def __init__(self, port):
        self.port = port
        self.server = socketserver.ThreadingUDPServer(('', port), UDPRequestHandler)

    def run(self):
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        print("%s server loop running in thread: %s" % (self.server.RequestHandlerClass.__name__[:3], thread.name))

        try:
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()

        except KeyboardInterrupt:
            pass
        finally:
            self.server.shutdown()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit("Invalid number of arguments")
    port = sys.argv[2]
    name = sys.argv[4]
    dns_server = DNSServer(int(port))
    dns_server.run()

