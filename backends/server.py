from http.server import ThreadingHTTPServer
from socket import socket
from typing import Any


class SpeculumServer(ThreadingHTTPServer):
    def __init__(
        self, server_address, RequestHandlerClass, base_url, no_cache, inject_nested
    ):
        self.base_url = base_url
        self.no_cache = no_cache
        self.inject_nested = inject_nested
        super().__init__(server_address, RequestHandlerClass)

    def finish_request(
        self, request: socket | tuple[bytes, socket], client_address: Any
    ) -> None:
        self.RequestHandlerClass(
            self.base_url,
            self.no_cache,
            self.inject_nested,
            request,
            client_address,
            self,
        )
