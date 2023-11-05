import socket
import ssl
from pathlib import Path


class SymbolPeerClient:
    def __init__(self, host: str, port: int, certificate_directory: str):
        (self.node_host, self.node_port) = (host, port)
        self.certificate_directory = Path(certificate_directory)
        self.timeout = 10

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.ssl_context.load_cert_chain(
            self.certificate_directory / "node.full.crt.pem",
            keyfile=self.certificate_directory / "node.key.pem",
        )

    def connection(self) -> ssl.SSLSocket:
        try:
            with socket.create_connection(
                (self.node_host, self.node_port), self.timeout
            ) as sock:
                return self.ssl_context.wrap_socket(sock)
        except socket.timeout as ex:
            raise ConnectionRefusedError from ex
