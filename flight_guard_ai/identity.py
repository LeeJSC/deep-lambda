"""Identity management for Flight Guard AI.

Provides helpers for loading keys, signing messages and verifying peer
certificates.  The implementation intentionally uses modern primitives
from the `cryptography` project to leverage well reviewed, open-source
code rather than bespoke cryptography.
"""
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519


@dataclass
class Identity:
    """Represents an aircraft cryptographic identity."""

    private_key: ed25519.Ed25519PrivateKey
    certificate: bytes  # DER or raw public key bytes
    x25519_private: x25519.X25519PrivateKey
    x25519_public: bytes

    @classmethod
    def generate(cls) -> "Identity":
        """Create fresh Ed25519 and X25519 key pairs."""
        priv = ed25519.Ed25519PrivateKey.generate()
        cert = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        x_priv = x25519.X25519PrivateKey.generate()
        x_pub = x_priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return cls(
            private_key=priv,
            certificate=cert,
            x25519_private=x_priv,
            x25519_public=x_pub,
        )

    def public_key_bytes(self) -> bytes:
        """Return the raw Ed25519 public key bytes for this identity."""
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def x25519_public_key_bytes(self) -> bytes:
        """Return the raw X25519 public key bytes."""
        return self.x25519_public

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
