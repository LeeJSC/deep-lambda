use ed25519_dalek::{SigningKey, VerifyingKey, Signature, Signer, Verifier};
use rand_core::{CryptoRng, RngCore};
use x25519_dalek::{StaticSecret, PublicKey};

/// Represents an aircraft cryptographic identity.
pub struct Identity {
    signing_key: SigningKey,
    pub cert: VerifyingKey,
    x25519_secret: StaticSecret,
    pub x25519_public: PublicKey,
}

impl Identity {
    /// Generate a new keypair using the provided RNG.
    pub fn generate<R: RngCore + CryptoRng>(rng: &mut R) -> Self {
        let signing_key = SigningKey::generate(rng);
        let cert = signing_key.verifying_key();
        let x25519_secret = StaticSecret::new(rng);
        let x25519_public = PublicKey::from(&x25519_secret);
        Self { signing_key, cert, x25519_secret, x25519_public }
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

    /// Perform Diffie-Hellman with our static X25519 secret.
    pub fn diffie_hellman(&self, peer: &PublicKey) -> [u8;32] {
        self.x25519_secret.diffie_hellman(peer).to_bytes()
    }
}
