from http.server import ThreadingHTTPServer
from socket import socket
from typing import Any


class SpeculumServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, base_url):
        self.base_url = base_url
        super().__init__(server_address, RequestHandlerClass)

    def finish_request(
        self, request: socket | tuple[bytes, socket], client_address: Any
    ) -> None:
        self.RequestHandlerClass(self.base_url, request, client_address, self)
