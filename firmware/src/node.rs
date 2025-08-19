use crate::{crypto, handshake, identity::Identity, packets::{DataPacket, DataRelayHeader, DataBody, SECTION_SIZE}};
use crate::radio::Radio;
use rand_core::{RngCore, CryptoRng};
use heapless::Vec;

pub struct Node<R: Radio, RNG: RngCore + CryptoRng> {
    radio: R,
    rng: RNG,
    identity: Identity,
    session_key: [u8;32],
}

impl<R: Radio, RNG: RngCore + CryptoRng> Node<R, RNG> {
    pub fn new(radio: R, mut rng: RNG) -> Self {
        let id = Identity::generate(&mut rng);
        // For demo purposes, self-derive session key using own X25519 key.
        let hs = handshake::initiate(&id, &id.x25519_public, &mut rng);

        Node { radio, rng, identity: id, session_key: hs.session_key }
    }

    pub fn send_dummy(&mut self) {
        let mut pkt = DataPacket {
            header: DataRelayHeader { timestamp_utc: 0, payload_hash: [0u8;32], relay_path: Vec::new() },
            body: DataBody::default(),
        };
        pkt.header.payload_hash = pkt.calc_hash();
        let mut buf: Vec<u8, {SECTION_SIZE*4}> = Vec::new();
        buf.extend_from_slice(&pkt.body.audio_enc).ok();
        crypto::encrypt_in_place(&self.session_key, &[0u8;12], &mut buf);
        self.radio.send(buf.as_slice());
    }
}
