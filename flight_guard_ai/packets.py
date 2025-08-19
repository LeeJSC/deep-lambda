"""Packet structures for Flight Guard AI."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import hashlib

from .identity import Identity

SECTION_SIZE = 4096


class MessageType(Enum):
    PING = 0x01
    PONG = 0x02
    DATA_RELAY = 0x03
    ACK = 0x04


@dataclass
class Ping:
    """Signed ping used for neighbor discovery."""

    aircraft_id: bytes
    nonce: bytes
    timestamp_utc: int
    signature: bytes = b""

    def to_bytes(self) -> bytes:
        return self.aircraft_id + self.nonce + self.timestamp_utc.to_bytes(8, "big")

    def sign(self, identity: Identity) -> None:
        self.signature = identity.sign(self.to_bytes())


@dataclass
class Pong(Ping):
    """Response to a :class:`Ping`.  Shares the same layout."""
    pass


@dataclass
class Ack:
    """Acknowledgment of a relay packet with time-of-flight."""

    payload_hash: bytes
    time_of_flight_ms: int
    timestamp_utc: int
    signature: bytes = b""

    def to_bytes(self) -> bytes:
        return (
            self.payload_hash
            + self.time_of_flight_ms.to_bytes(4, "big")
            + self.timestamp_utc.to_bytes(8, "big")
        )

    def sign(self, identity: Identity) -> None:
        self.signature = identity.sign(self.to_bytes())


@dataclass
class RelayPathEntry:
    aircraft_id: bytes
    hop_number: int


@dataclass
class DataBody:
    """Four encrypted sections: audio, log, and two decoys."""
    audio_enc: bytes = field(default_factory=lambda: b"".ljust(SECTION_SIZE, b"\x00"))
    log_enc: bytes = field(default_factory=lambda: b"".ljust(SECTION_SIZE, b"\x00"))
    decoy1_enc: bytes = field(default_factory=lambda: b"".ljust(SECTION_SIZE, b"\x00"))
    decoy2_enc: bytes = field(default_factory=lambda: b"".ljust(SECTION_SIZE, b"\x00"))


@dataclass
class DataRelayHeader:
    message_type: MessageType
    timestamp_utc: int
    payload_hash: bytes
    relay_path: List[RelayPathEntry] = field(default_factory=list)


@dataclass
class DataPacket:
    header: DataRelayHeader
    body: DataBody

    def calc_hash(self) -> bytes:
        """Return a BLAKE2s hash over deterministically serialized fields."""
        h = hashlib.blake2s()
        h.update(self.header.message_type.value.to_bytes(1, "big"))
        h.update(self.header.timestamp_utc.to_bytes(8, "big"))
        for entry in self.header.relay_path:
            h.update(entry.aircraft_id)
            h.update(entry.hop_number.to_bytes(2, "big"))
        h.update(self.body.audio_enc)
        h.update(self.body.log_enc)
        h.update(self.body.decoy1_enc)
        h.update(self.body.decoy2_enc)
        return h.digest()
