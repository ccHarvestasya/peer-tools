import ssl
from symbolchain.BufferReader import BufferReader
from symbolpeer.CreatorBase import CreatorBase

NODE_DISCOVERY_PULL_PEERS = 0x113


class NodeDiscoveryPullPeers:
    def __init__(self):
        self.version = 0
        self.publicKey = ""
        self.networkGenerationHashSeed = ""
        self.roles = 0
        self.port = 0
        self.networkIdentifier = 0
        self.host = ""
        self.friendlyName = ""


class NodePeersCreator(CreatorBase):
    def create(self, ssocket: ssl.SSLSocket) -> list[NodeDiscoveryPullPeers]:
        """NodePeers データ作成"""
        # NODE_DISCOVERY_PULL_PING リクエスト
        self._send_simple_request(ssocket, NODE_DISCOVERY_PULL_PEERS)
        # NODE_DISCOVERY_PULL_PING レスポンスを読み込み
        reader = self._read_packet_data(ssocket, NODE_DISCOVERY_PULL_PEERS)
        # NodePeers データ作成
        return self._parse_node_discovery_pull_peers_response(reader)

    def _parse_node_discovery_pull_peers_response(
        self, reader: BufferReader
    ) -> list[NodeDiscoveryPullPeers]:
        """NODE_DISCOVERY_PULL_PEERS パース"""
        node_discovery_pull_peers_list = []
        while not reader.eof:
            node_discovery_pull_peers = NodeDiscoveryPullPeers()
            reader.read_int(4)
            node_discovery_pull_peers.version = reader.read_int(4)
            node_discovery_pull_peers.publicKey = reader.read_hex_string(32)
            node_discovery_pull_peers.networkGenerationHashSeed = (
                reader.read_hex_string(32)
            )
            node_discovery_pull_peers.roles = reader.read_int(4)
            node_discovery_pull_peers.port = reader.read_int(2)
            node_discovery_pull_peers.networkIdentifier = reader.read_int(1)
            host_length = reader.read_int(1)
            friendly_name_length = reader.read_int(1)
            node_discovery_pull_peers.host = reader.read_string(host_length)
            node_discovery_pull_peers.friendlyName = reader.read_string(
                friendly_name_length
            )
            node_discovery_pull_peers_list.append(node_discovery_pull_peers)
        return node_discovery_pull_peers_list
