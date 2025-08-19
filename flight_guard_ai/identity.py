"""Identity management for Flight Guard AI.


Provides helpers for loading keys, signing messages and verifying peer
certificates.  The implementation intentionally uses modern primitives
from the `cryptography` project to leverage well reviewed, open-source
code rather than bespoke cryptography.
"""
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519



@dataclass
class Identity:
    """Represents an aircraft cryptographic identity."""

    private_key: ed25519.Ed25519PrivateKey
    certificate: bytes  # DER or raw public key bytes

    @classmethod
    def generate(cls) -> "Identity":
        """Create a fresh Ed25519 key pair and self-signed certificate."""
        priv = ed25519.Ed25519PrivateKey.generate()
        cert = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return cls(private_key=priv, certificate=cert)

    def public_key_bytes(self) -> bytes:
        """Return the raw public key bytes for this identity."""
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign(self, message: bytes) -> bytes:
        """Sign a message using the private key."""
        return self.private_key.sign(message)

    @staticmethod
    def verify_peer(cert: bytes, message: bytes, signature: bytes) -> bool:
        """Verify a peer certificate against a signature.

        A real system would additionally consult a revocation list.  Here we
        simply check that the signature validates under the provided public
        key bytes.
        """
        try:
            pub = ed25519.Ed25519PublicKey.from_public_bytes(cert)
            pub.verify(signature, message)
            return True
        except Exception:
            return False

