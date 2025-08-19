"""Packet structures for Flight Guard AI."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import hashlib

SECTION_SIZE = 4096


class MessageType(Enum):
    PING = 0x01
    PONG = 0x02
    DATA_RELAY = 0x03
    ACK = 0x04


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
        """Return a BLAKE2s hash over header and body."""
        h = hashlib.blake2s()
        h.update(str(self.header).encode())
        h.update(self.body.audio_enc)
        h.update(self.body.log_enc)
        h.update(self.body.decoy1_enc)
        h.update(self.body.decoy2_enc)
        return h.digest()
