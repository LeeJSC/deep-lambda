"""Cryptographic helper functions."""
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


def encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    """Encrypt data using ChaCha20-Poly1305.

    Returns a tuple of (ciphertext, tag) so callers can store the
    authentication tag separately from the ciphertext.
    """
    aead = ChaCha20Poly1305(key)
    ct = aead.encrypt(nonce, plaintext, b"")
    return ct[:-16], ct[-16:]


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
    """Decrypt data previously produced by :func:`encrypt`."""
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ciphertext + tag, b"")
