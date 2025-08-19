"""Relay logic for forwarding packets between aircraft."""
from dataclasses import dataclass, field
from typing import Dict
from .packets import DataPacket, RelayPathEntry, MessageType


@dataclass
class NeighborInfo:
    last_seen: int
    rtt_ms: int


@dataclass
class RelayNode:
    neighbors: Dict[bytes, NeighborInfo] = field(default_factory=dict)

    def handle_packet(self, pkt: DataPacket) -> None:
        """Process an incoming packet and forward or deliver."""
        raise NotImplementedError("Relay logic not implemented")

    def send_ack(self, payload_hash: bytes, tof_ms: int) -> None:
        """Send an acknowledgment for a received packet."""
        raise NotImplementedError("ACK send not implemented")

    def monitor_latency(self) -> None:
        """Check time-of-flight and seek better neighbors if needed."""
        raise NotImplementedError("Latency monitoring not implemented")
