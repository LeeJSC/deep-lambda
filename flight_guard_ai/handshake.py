"""Handshake routines using Noise-like patterns.

The real system can be mapped onto the Noise IK pattern used by
WireGuard.  For demonstrative purposes we implement a minimal
authenticated X25519 exchange that derives a symmetric session key and
proves identity by signing the ephemeral public key.
"""
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .identity import Identity


@dataclass
class HandshakeResult:
    """Outcome of a handshake.

    `eph_public` and `signature` should be sent to the peer who can verify
    them against the certificate embedded in the ping/pong exchange.
    """

    session_key: bytes
    eph_public: bytes
    signature: bytes


def initiate_handshake(identity: Identity, peer_public_key: bytes) -> HandshakeResult:
    """Perform an authenticated X25519 key exchange.

    The caller supplies the peer's X25519 public key (usually learned from
    its certificate).  The resulting session key is suitable for symmetric
    encryption with ChaCha20-Poly1305.
    """
    eph_priv = x25519.X25519PrivateKey.generate()
    peer_pub = x25519.X25519PublicKey.from_public_bytes(peer_public_key)
    shared = eph_priv.exchange(peer_pub)

    session_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"flight-guard-ai",
    ).derive(shared)

    eph_public = eph_priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    signature = identity.sign(eph_public)

    return HandshakeResult(
        session_key=session_key,
        eph_public=eph_public,
        signature=signature,
    )
