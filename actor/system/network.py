import socketserver
import ssl
import re


class MsgHandler(socketserver.StreamRequestHandler):
    def handle(self):
        msg = b""
        while not re.search(b":end:$", msg):
            msg += self.request.recv(1024)
        print(msg)


class TLSServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(self, server_address, RequestHandlerClass)
        # add TLS support
        self.socket = socket.socket(self.address_family, self.socket_type)
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise
