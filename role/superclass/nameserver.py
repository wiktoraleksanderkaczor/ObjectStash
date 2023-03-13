"""
DNS service for cluster and caching.
"""
import dnslib
import dnslib.server
from dnslib import DNSRecord
from dnslib.server import DNSHandler


class MyDNSServer(dnslib.server.BaseResolver):
    def resolve(self, request: DNSRecord, handler: DNSHandler):
        reply = request.reply()
        qname = request.q.qname
        qtype = request.q.qtype

        # Here you can implement your own logic for handling DNS queries
        # For example, you can use a dictionary to map domain names to IP addresses
        # and return the appropriate IP address for each query

        # Example code for mapping 'example.com' to '127.0.0.1'
        if qname == dnslib.DNSLabel("example.com") and qtype == dnslib.QTYPE.A:
            reply.add_answer(dnslib.RR(qname, dnslib.QTYPE.A, rdata=dnslib.A("127.0.0.1")))
            return reply

        # If the query does not match any of the rules above, return a NXDOMAIN response
        reply.header.rcode = dnslib.RCODE.NXDOMAIN
        return reply


server = dnslib.server.DNSServer(MyDNSServer())
server.start()
