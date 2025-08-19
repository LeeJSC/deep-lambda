"""Cryptographic helper functions."""
from typing import Tuple


def encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    """Encrypt data using an AEAD cipher.

    Returns a tuple of (ciphertext, tag). This is a stub implementation.
    """
    raise NotImplementedError("Encryption not implemented")


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
    """Decrypt data using an AEAD cipher."""
    raise NotImplementedError("Decryption not implemented")
