import os
import sys
import socket
import ssl
import OpenSSL
from pathlib import Path
from symbolchain.BufferReader import BufferReader
from symbolchain.BufferWriter import BufferWriter

CERTIFICATE_DIRECTORY = os.getcwd() + "/cert"

CHAIN_STATISTICS = 5
NODE_DISCOVERY_PULL_PING = 0x111
NODE_DISCOVERY_PULL_PEERS = 0x113
UNLOCKED_ACCOUNTS = 0x304

x509 = None
pubkey_str = ""


class ChainStatistics:
    def __init__(self):
        self.height = 0
        self.finalized_height = 0
        self.score_high = 0
        self.score_low = 0

    def __str__(self):
        score = self.score_high << 64 | self.score_low
        return "\n".join(
            [
                f"          height: {self.height}",
                f"finalized height: {self.finalized_height}",
                f"           score: {score}",
            ]
        )


class NodeDiscoveryPullPing:
    def __init__(self):
        self.version = 0
        self.public_key = ""
        self.network_generation_hash_seed = ""
        self.roles = 0
        self.port = 0
        self.network_identifier = 0
        self.host = ""
        self.friendly_name = ""
        self.node_public_key = ""

    def __str__(self):
        return "\n".join(
            [
                f"                     version: {self.version}",
                f"                  public key: {self.public_key}",
                f"network generation hash seed: {self.network_generation_hash_seed}",
                f"                       roles: {self.roles}",
                f"                        port: {self.port}",
                f"          network_identifier: {self.network_identifier}",
                f"                        host: {self.host}",
                f"               friendly_name: {self.friendly_name}",
                f"             node_public_key: {self.node_public_key}",
            ]
        )


class NodeDiscoveryPullPeers:
    def __init__(self):
        self.version = 0
        self.public_key = ""
        self.network_generation_hash_seed = ""
        self.roles = 0
        self.port = 0
        self.network_identifier = 0
        self.host = ""
        self.friendly_name = ""

    def __str__(self):
        return "\n".join(
            [
                f"                     version: {self.version}",
                f"                  public key: {self.public_key}",
                f"network generation hash seed: {self.network_generation_hash_seed}",
                f"                       roles: {self.roles}",
                f"                        port: {self.port}",
                f"          network_identifier: {self.network_identifier}",
                f"                        host: {self.host}",
                f"               friendly_name: {self.friendly_name}",
            ]
        )


class UnlockedAccounts:
    def __init__(self):
        self.unlocked_account = ""

    def __str__(self):
        return "\n".join(
            [
                f"unlockedAccount: {self.unlocked_account}",
            ]
        )


class SymbolPeerClient:
    def __init__(self, host, port, certificate_directory):
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

    def _send_socket_request(self, packet_type, parser):
        try:
            with socket.create_connection(
                (self.node_host, self.node_port), self.timeout
            ) as sock:
                with self.ssl_context.wrap_socket(sock) as ssock:
                    self._send_simple_request(ssock, packet_type)
                    return parser(self._read_packet_data(ssock, packet_type))
        except socket.timeout as ex:
            raise ConnectionRefusedError from ex

    @staticmethod
    def _send_simple_request(ssock, packet_type):
        writer = BufferWriter()
        writer.write_int(8, 4)
        writer.write_int(packet_type, 4)
        ssock.send(writer.buffer)

    def _read_packet_data(self, ssock, packet_type):
        read_buffer = ssock.read()

        if 0 == len(read_buffer):
            raise ConnectionRefusedError(
                f"socket returned empty data for {self.node_host}"
            )

        size = BufferReader(read_buffer).read_int(4)

        while len(read_buffer) < size:
            read_buffer += ssock.read()

        # ついでに証明書取得
        global pubkey_str
        global x509
        der_cert = ssock.getpeercert(True)
        cert = ssl.DER_cert_to_PEM_cert(der_cert)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        pubkey = OpenSSL.crypto.dump_publickey(
            OpenSSL.crypto.FILETYPE_ASN1, x509.get_pubkey()
        )
        pubkey_str = pubkey.hex().removeprefix("302a300506032b6570032100")  # 要らない部分除去
        pubkey_str = pubkey_str.upper()
        # read_buffer += bytes.fromhex(pubkey_str)  # 末尾にセット

        reader = BufferReader(read_buffer)
        size = reader.read_int(4)
        actual_packet_type = reader.read_int(4)

        if packet_type != actual_packet_type:
            raise ConnectionRefusedError(
                f"socket returned packet type {actual_packet_type} but expected {packet_type}"
            )

        return reader

    def get_chain_statistics(self):
        packet_type = CHAIN_STATISTICS
        return self._send_socket_request(
            packet_type, self._parse_chain_statistics_response
        )

    def get_node_discovery_pull_ping(self):
        packet_type = NODE_DISCOVERY_PULL_PING
        return self._send_socket_request(
            packet_type, self._node_discovery_pull_ping_response
        )

    def get_node_discovery_pull_peers(self):
        packet_type = NODE_DISCOVERY_PULL_PEERS
        return self._send_socket_request(
            packet_type, self._node_discovery_pull_peers_response
        )

    def get_unlocked_accounts(self):
        packet_type = UNLOCKED_ACCOUNTS
        return self._send_socket_request(packet_type, self._unlocked_accounts_response)

    @staticmethod
    def _parse_chain_statistics_response(reader):
        chain_statistics = ChainStatistics()

        chain_statistics.height = reader.read_int(8)
        chain_statistics.finalized_height = reader.read_int(8)
        chain_statistics.score_high = reader.read_int(8)
        chain_statistics.score_low = reader.read_int(8)

        return chain_statistics

    @staticmethod
    def _node_discovery_pull_ping_response(reader):
        node_discovery_pull_ping = NodeDiscoveryPullPing()

        reader.read_int(4)
        node_discovery_pull_ping.version = reader.read_int(4)
        node_discovery_pull_ping.public_key = reader.read_hex_string(32)
        node_discovery_pull_ping.network_generation_hash_seed = reader.read_hex_string(
            32
        )
        node_discovery_pull_ping.roles = reader.read_int(4)
        node_discovery_pull_ping.port = reader.read_int(2)
        node_discovery_pull_ping.network_identifier = reader.read_int(1)
        host_length = reader.read_int(1)
        friendly_name_length = reader.read_int(1)
        node_discovery_pull_ping.host = reader.read_string(host_length)
        node_discovery_pull_ping.friendly_name = reader.read_string(
            friendly_name_length
        )

        node_discovery_pull_ping.node_public_key = pubkey_str

        return node_discovery_pull_ping

    @staticmethod
    def _node_discovery_pull_peers_response(reader):
        node_discovery_pull_peers_list = []

        while not reader.eof:
            node_discovery_pull_peers = NodeDiscoveryPullPeers()
            reader.read_int(4)
            node_discovery_pull_peers.version = reader.read_int(4)
            node_discovery_pull_peers.public_key = reader.read_hex_string(32)
            node_discovery_pull_peers.network_generation_hash_seed = (
                reader.read_hex_string(32)
            )
            node_discovery_pull_peers.roles = reader.read_int(4)
            node_discovery_pull_peers.port = reader.read_int(2)
            node_discovery_pull_peers.network_identifier = reader.read_int(1)
            host_length = reader.read_int(1)
            friendly_name_length = reader.read_int(1)
            node_discovery_pull_peers.host = reader.read_string(host_length)
            node_discovery_pull_peers.friendly_name = reader.read_string(
                friendly_name_length
            )
            node_discovery_pull_peers_list.append(node_discovery_pull_peers)

        return node_discovery_pull_peers_list

    @staticmethod
    def _unlocked_accounts_response(reader):
        unlocked_accounts_list = []

        while not reader.eof:
            unlocked_accounts = UnlockedAccounts()
            unlocked_accounts.unlocked_account = reader.read_hex_string(32)
            unlocked_accounts_list.append(unlocked_accounts)

        return unlocked_accounts_list


def main(argv):
    command = ""
    hostname = "127.0.0.1"
    port = 7900
    if 2 > len(argv):
        print()
        print(os.path.basename(__file__) + " COMMAND HOSTNAME [PORT]")
        print()
        print("COMMANDS")
        print("  chainInfo\t\t\t/chain/info")
        print("  nodeInfo\t\t\t/node/info")
        print("  nodePeers\t\t\t/node/peers")
        print("  nodeUnlockedaccount\t\t/node/unlockedaccount")
        print()
        return 0
    elif 4 <= len(argv):
        if not argv[3].isdigit():
            print("argument is not digit")
            return 1
        port = argv[3]

    command = argv[1]
    hostname = argv[2]

    # print("COMMAND=" + command + ", HOSTNAME=" + hostname + ", PORT=" + str(port))

    peer_client = SymbolPeerClient(hostname, port, CERTIFICATE_DIRECTORY)
    if command == "chainInfo" or command == "ci":
        result = peer_client.get_chain_statistics()
        print(result)
    elif command == "nodeInfo" or command == "ni":
        result = peer_client.get_node_discovery_pull_ping()
        print(result)
    elif command == "nodePeers" or command == "np":
        results = peer_client.get_node_discovery_pull_peers()
        for result in results:
            print(result)
            print()
    elif command == "nodeUnlockedaccount" or command == "nu":
        result = peer_client.get_unlocked_accounts()
        for result in results:
            print(result)
            print()
    else:
        print("unknown command")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as ex:
        print(ex)
