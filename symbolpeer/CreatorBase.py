import ssl
from symbolchain.BufferReader import BufferReader
from symbolchain.BufferWriter import BufferWriter


class CreatorBase:
    def _send_simple_request(self, ssocket: ssl.SSLSocket, packet_type: int):
        writer = BufferWriter()
        writer.write_int(8, 4)
        writer.write_int(packet_type, 4)
        ssocket.send(writer.buffer)

    def _read_packet_data(self, ssock, packet_type):
        read_buffer = ssock.read()

        if 0 == len(read_buffer):
            # レスポンスが空
            raise ConnectionRefusedError(f"socket returned empty data")

        # レスポンスを全部読み込む
        size = BufferReader(read_buffer).read_int(4)
        while len(read_buffer) < size:
            read_buffer += ssock.read()

        # 期待したソケットタイプか確認
        reader = BufferReader(read_buffer)
        size = reader.read_int(4)
        actual_packet_type = reader.read_int(4)
        if packet_type != actual_packet_type:
            # 期待したソケットタイプではなかった場合
            raise ConnectionRefusedError(
                f"socket returned packet type {actual_packet_type} but expected {packet_type}"
            )

        return reader
