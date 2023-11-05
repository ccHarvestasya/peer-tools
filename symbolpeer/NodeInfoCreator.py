import ssl
import OpenSSL
from symbolchain.BufferReader import BufferReader

from symbolpeer.CreatorBase import CreatorBase

NODE_DISCOVERY_PULL_PING = 0x111


class NodeDiscoveryPullPing:
    def __init__(self):
        self.version = 0
        self.publicKey = ""
        self.networkGenerationHashSeed = ""
        self.roles = 0
        self.port = 0
        self.networkIdentifier = 0
        self.host = ""
        self.friendlyName = ""
        self.nodePublicKey = ""


class NodeInfoCreator(CreatorBase):
    def create(self, ssocket: ssl.SSLSocket) -> NodeDiscoveryPullPing:
        """NodeInfo データ作成"""
        # NODE_DISCOVERY_PULL_PING リクエスト
        self._send_simple_request(ssocket, NODE_DISCOVERY_PULL_PING)
        # NODE_DISCOVERY_PULL_PING レスポンスを読み込み
        reader = self._read_packet_data(ssocket, NODE_DISCOVERY_PULL_PING)
        # ノード証明書取得
        node_public_key = self._get_node_public_key(ssocket)
        # NodeInfo データ作成
        return self._parse_node_discovery_pull_ping_response(reader, node_public_key)

    def _parse_node_discovery_pull_ping_response(
        self, reader: BufferReader, node_public_key: str
    ) -> NodeDiscoveryPullPing:
        """NodeDiscoveryPullPing パース"""
        reader.offset = 12  # 先頭4バイトは使用しない

        node_discovery_pull_ping = NodeDiscoveryPullPing()
        node_discovery_pull_ping.version = reader.read_int(4)
        node_discovery_pull_ping.publicKey = reader.read_hex_string(32)
        node_discovery_pull_ping.networkGenerationHashSeed = reader.read_hex_string(32)
        node_discovery_pull_ping.roles = reader.read_int(4)
        node_discovery_pull_ping.port = reader.read_int(2)
        node_discovery_pull_ping.networkIdentifier = reader.read_int(1)

        host_length = reader.read_int(1)
        friendly_name_length = reader.read_int(1)
        node_discovery_pull_ping.host = reader.read_string(host_length)
        node_discovery_pull_ping.friendlyName = reader.read_string(friendly_name_length)

        node_discovery_pull_ping.nodePublicKey = node_public_key

        return node_discovery_pull_ping

    def _get_node_public_key(self, ssocket: ssl.SSLSocket) -> str:
        """ノード証明書取得"""
        der_cert = ssocket.getpeercert(True)
        cert = ssl.DER_cert_to_PEM_cert(der_cert)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        pubkey = OpenSSL.crypto.dump_publickey(
            OpenSSL.crypto.FILETYPE_ASN1, x509.get_pubkey()
        )
        pubkey_str = pubkey.hex().removeprefix("302a300506032b6570032100")  # 要らない部分除去
        pubkey_str = pubkey_str.upper()

        return pubkey_str
