use ed25519_dalek::{SigningKey, VerifyingKey, Signature, Signer, Verifier};
use rand_core::{CryptoRng, RngCore};

/// Represents an aircraft cryptographic identity.
pub struct Identity {
    signing_key: SigningKey,
    pub cert: VerifyingKey,
}

impl Identity {
    /// Generate a new keypair using the provided RNG.
    pub fn generate<R: RngCore + CryptoRng>(rng: &mut R) -> Self {
        let signing_key = SigningKey::generate(rng);
        let cert = signing_key.verifying_key();
        Self { signing_key, cert }
    }

    /// Sign a message.
    pub fn sign(&self, msg: &[u8]) -> Signature {
        self.signing_key.sign(msg)
    }

    /// Verify a message and signature against a certificate.
    pub fn verify(cert: &VerifyingKey, msg: &[u8], sig: &Signature) -> bool {
        cert.verify(msg, sig).is_ok()
    }

    /// Return raw public key bytes.
    pub fn public_key(&self) -> [u8; 32] {
        self.cert.to_bytes()
    }
}
