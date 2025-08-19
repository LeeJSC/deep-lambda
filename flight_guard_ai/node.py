"""Main event loop tying together handshake, relay, and packet I/O."""

import time

from .identity import Identity
from .packets import DataBody, DataPacket, DataRelayHeader, MessageType
from .relay import NeighborInfo, RelayNode


def main() -> None:
    """Entry point for the Flight Guard AI node.

    This demo builds a dummy data packet, processes it locally, and
    exercises the relay's latency monitoring which in turn emits a
    signed ping to a fictitious neighbor.
    """

    identity = Identity.generate()
    node = RelayNode(identity=identity)

    header = DataRelayHeader(
        message_type=MessageType.DATA_RELAY,
        timestamp_utc=int(time.time()),
        payload_hash=b"",
    )
    packet = DataPacket(header=header, body=DataBody())
    packet.header.payload_hash = packet.calc_hash()
    node.handle_packet(packet)

    dummy_peer = b"\x00" * 32
    node.neighbors[dummy_peer] = NeighborInfo(last_seen=int(time.time()), rtt_ms=6000)
    node.monitor_latency()

