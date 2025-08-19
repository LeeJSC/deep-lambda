"""Relay logic for forwarding packets between aircraft."""
from dataclasses import dataclass, field
from typing import Dict, Tuple
import os
import socket
import time

from .identity import Identity
from .packets import Ack, DataPacket, RelayPathEntry, Ping


@dataclass
class NeighborInfo:
    last_seen: int
    rtt_ms: int
    addr: Tuple[str, int]


@dataclass
class RelayNode:
    """Minimal relay node implementation."""

    identity: Identity
    neighbors: Dict[bytes, NeighborInfo] = field(default_factory=dict)

    def handle_packet(self, pkt: DataPacket, addr: Tuple[str, int]) -> None:
        """Process an incoming packet and send an ACK.

        This function appends the node's identity to the relay path and
        responds with an acknowledgment containing the measured
        time-of-flight.  Forwarding to the next hop is transport specific
        and therefore omitted here.
        """

        sender_id = pkt.header.relay_path[-1].aircraft_id if pkt.header.relay_path else b""
        hop_no = len(pkt.header.relay_path) + 1
        pkt.header.relay_path.append(
            RelayPathEntry(self.identity.public_key_bytes(), hop_no)
        )

        now = int(time.time())
        tof_ms = int((now - pkt.header.timestamp_utc) * 1000)
        if sender_id:
            self.neighbors[sender_id] = NeighborInfo(
                last_seen=now, rtt_ms=tof_ms, addr=addr
            )
        self.send_ack(pkt.header.payload_hash, tof_ms, addr)

    def send_ack(self, payload_hash: bytes, tof_ms: int, addr: Tuple[str, int]) -> None:
        """Send an acknowledgment for a received packet.

        The ACK is signed so the previous hop can authenticate the
        response.
        """

        ack = Ack(
            payload_hash=payload_hash,
            time_of_flight_ms=tof_ms,
            timestamp_utc=int(time.time()),
        )
        ack.sign(self.identity)
        data = ack.to_bytes() + ack.signature
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, addr)

    def send_ping(self, peer: bytes) -> None:
        """Send a signed ping to a neighbor."""
        info = self.neighbors.get(peer)
        if info is None:
            return
        nonce = os.urandom(32)
        ping = Ping(
            aircraft_id=self.identity.public_key_bytes(),
            nonce=nonce,
            timestamp_utc=int(time.time()),
        )
        ping.sign(self.identity)
        data = ping.to_bytes() + ping.signature
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, info.addr)

    def monitor_latency(self) -> None:
        """Check time-of-flight and seek better neighbors if needed."""
        for peer, info in list(self.neighbors.items()):
            if info.rtt_ms > 5000:
                self.send_ping(peer)
