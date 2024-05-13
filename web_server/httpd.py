import sys
from http import HTTPStatus
from optparse import OptionParser
from socketserver import (
    TCPServer,
    BaseRequestHandler,
)

from enums import (
    RequestHeaders,
    RequestMethods,
)

ALLOWED_METHODS = set(RequestMethods)


class TCPHandler(BaseRequestHandler):
    def handle(self):
        recieved_data = str(self.request.recv(1024), 'utf-8')
        method, url, *_ = recieved_data.split()
        if method not in ALLOWED_METHODS:
            response = self._response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.request.sendall(response.encode())
        else:
            response = self._response(HTTPStatus.OK) + self._headers()
            print(response)
            self.request.send(response.encode('utf-8'))
        self.request.close()

    def _response(self, http_status: HTTPStatus) -> str:
        return f'HTTP/1.1 {http_status.value} {http_status.name}\r\n'

    def _headers(self) -> str:
        headers = {
            RequestHeaders.SERVER: 'localhost',
            RequestHeaders.CONTENT_TYPE: 'text/html; encoding=utf8',
        }
        return ''.join(f'{k}: {v}\r\n' for k, v in headers.items())


class Server(TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler):
        TCPServer.__init__(self, server_address, handler)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-r", "--root", action="store", default='documents')
    opts, args = op.parse_args()

    address = ('localhost', 80)
    server = Server(address, TCPHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
