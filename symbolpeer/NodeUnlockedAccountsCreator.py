import ssl
from symbolchain.BufferReader import BufferReader
from symbolpeer.CreatorBase import CreatorBase

UNLOCKED_ACCOUNTS = 0x304


class NodeUnlockedAccount:
    def __init__(self):
        self.unlockedAccount = []


class NodeUnlockedAccountCreator(CreatorBase):
    def create(self, ssocket: ssl.SSLSocket) -> NodeUnlockedAccount:
        """NodeUnlockedAccount データ作成"""
        # UNLOCKED_ACCOUNTS リクエスト
        self._send_simple_request(ssocket, UNLOCKED_ACCOUNTS)
        # UNLOCKED_ACCOUNTS レスポンスを読み込み
        reader = self._read_packet_data(ssocket, UNLOCKED_ACCOUNTS)
        # NodeUnlockedAccount データ作成
        return self._parse_unlocked_accounts_response(reader)

    def _parse_unlocked_accounts_response(
        self, reader: BufferReader
    ) -> NodeUnlockedAccount:
        """UNLOCKED_ACCOUNTS パース"""
        node_unlocked_account = NodeUnlockedAccount()
        while not reader.eof:
            node_unlocked_account.unlockedAccount.append(reader.read_hex_string(32))
        return node_unlocked_account
