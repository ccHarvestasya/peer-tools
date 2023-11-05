import ssl
from symbolchain.BufferReader import BufferReader
from symbolpeer.CreatorBase import CreatorBase

CHAIN_STATISTICS = 5
FINALIZATION_STATISTICS = 0x132


class ChainStatistics:
    def __init__(self):
        self.height = 0
        self.finalized_height = 0
        self.score_high = 0
        self.score_low = 0


class FinalizationStatistics:
    def __init__(self):
        self.epoch = 0
        self.point = 0
        self.height = 0
        self.hash = ""


class ChainInfo:
    class FinalizedBlock:
        def __init__(self):
            self.finalizationEpoch = 0
            self.finalizationPoint = 0
            self.height = 0
            self.hash = 0

    def __init__(self):
        self.height = 0
        self.scoreHigh = 0
        self.scoreLow = 0
        self.latestFinalizedBlock = self.FinalizedBlock()


class ChainInfoCreator(CreatorBase):
    def create(self, ssocket: ssl.SSLSocket):
        """ChainInfo データ作成"""
        # CHAIN_STATISTICS リクエスト
        self._send_simple_request(ssocket, CHAIN_STATISTICS)
        # CHAIN_STATISTICS レスポンスを読み込み
        cs_reader = self._read_packet_data(ssocket, CHAIN_STATISTICS)
        # CHAIN_STATISTICS データ作成
        cs = self._parse_chain_statistics_response(cs_reader)

        # FINALIZATION_STATISTICS リクエスト
        self._send_simple_request(ssocket, FINALIZATION_STATISTICS)
        # FINALIZATION_STATISTICS レスポンスを読み込み
        fs_reader = self._read_packet_data(ssocket, FINALIZATION_STATISTICS)
        # FINALIZATION_STATISTICS データ作成
        fs = self._parse_finalization_statistics_response(fs_reader)

        # ChainInfo データ作成
        ci = ChainInfo()
        ci.height = cs.height
        ci.scoreHigh = cs.score_high
        ci.scoreLow = cs.score_low
        ci.latestFinalizedBlock.finalizationEpoch = fs.epoch
        ci.latestFinalizedBlock.finalizationPoint = fs.point
        ci.latestFinalizedBlock.height = fs.height
        ci.latestFinalizedBlock.hash = fs.hash

        return ci

    def _parse_chain_statistics_response(self, reader: BufferReader) -> ChainStatistics:
        """CHAIN_STATISTICS パース"""
        chain_statistics = ChainStatistics()
        chain_statistics.height = reader.read_int(8)
        chain_statistics.finalized_height = reader.read_int(8)
        chain_statistics.score_high = reader.read_int(8)
        chain_statistics.score_low = reader.read_int(8)
        return chain_statistics

    def _parse_finalization_statistics_response(
        self, reader: BufferReader
    ) -> FinalizationStatistics:
        """FINALIZATION_STATISTICS パース"""
        finalization_statistics = FinalizationStatistics()
        finalization_statistics.epoch = reader.read_int(4)
        finalization_statistics.point = reader.read_int(4)
        finalization_statistics.height = reader.read_int(8)
        finalization_statistics.hash = reader.read_hex_string(32)
        return finalization_statistics
