use chacha20poly1305::{aead::{AeadInPlace, KeyInit}, ChaCha20Poly1305, Key, Nonce};
use heapless::Vec;

/// Encrypt data in place using ChaCha20-Poly1305.
pub fn encrypt_in_place<const N: usize>(key: &[u8; 32], nonce: &[u8; 12], buf: &mut Vec<u8, N>) {
    let cipher = ChaCha20Poly1305::new(Key::from_slice(key));
    let nonce = Nonce::from_slice(nonce);
    let _ = cipher.encrypt_in_place(nonce, b"", buf);
}

/// Decrypt data in place.
pub fn decrypt_in_place<const N: usize>(key: &[u8; 32], nonce: &[u8; 12], buf: &mut Vec<u8, N>) -> bool {
    let cipher = ChaCha20Poly1305::new(Key::from_slice(key));
    let nonce = Nonce::from_slice(nonce);
    cipher.decrypt_in_place(nonce, b"", buf).is_ok()
}
