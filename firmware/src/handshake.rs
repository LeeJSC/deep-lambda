use blake3;
use x25519_dalek::{PublicKey, StaticSecret};
use rand_core::{CryptoRng, RngCore};
use ed25519_dalek::{Signature, VerifyingKey};
use crate::identity::Identity;

pub struct HandshakeResult {
    pub session_key: [u8; 32],
    pub eph_pubkey: [u8; 32],
    pub signature: Signature,
}

/// Perform an authenticated X25519 exchange.
pub fn initiate<R: RngCore + CryptoRng>(
    id: &Identity,
    peer_pubkey: &PublicKey,
    rng: &mut R,
) -> HandshakeResult {
    let eph_secret = StaticSecret::new(rng);
    let eph_public = PublicKey::from(&eph_secret);
    let shared = eph_secret.diffie_hellman(peer_pubkey);
    let session_key = blake3::derive_key("flight-guard-ai", shared.as_bytes());
    let signature = id.sign(eph_public.as_bytes());
    HandshakeResult {
        session_key,
        eph_pubkey: *eph_public.as_bytes(),
        signature,
    }
}


/// Respond to a handshake initiated by a peer.
/// Returns the derived session key if the signature verifies.
pub fn respond(
    id: &Identity,
    peer_eph_pubkey: &PublicKey,
    signature: &Signature,
    peer_cert: &VerifyingKey,
) -> Option<[u8; 32]> {
    if !Identity::verify(peer_cert, peer_eph_pubkey.as_bytes(), signature) {
        return None;
    }
    let shared = id.diffie_hellman(peer_eph_pubkey);
    Some(blake3::derive_key("flight-guard-ai", &shared))
}

