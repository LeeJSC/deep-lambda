use heapless::Vec;
use blake3::Hasher;

pub const SECTION_SIZE: usize = 4096;

#[derive(Clone, Copy)]
pub enum MessageType {
    Ping = 0x01,
    Pong = 0x02,
    DataRelay = 0x03,
    Ack = 0x04,
}

pub struct Ping {
    pub aircraft_id: [u8; 32],
    pub nonce: [u8; 32],
    pub timestamp_utc: u64,
    pub signature: [u8; 64],
}

pub type Pong = Ping;

pub struct Ack {
    pub payload_hash: [u8; 32],
    pub time_of_flight_ms: u32,
    pub timestamp_utc: u64,
    pub signature: [u8; 64],
}

pub struct RelayPathEntry {
    pub aircraft_id: [u8; 32],
    pub hop_number: u16,
}

pub struct DataBody {
    pub audio_enc: [u8; SECTION_SIZE],
    pub log_enc: [u8; SECTION_SIZE],
    pub decoy1_enc: [u8; SECTION_SIZE],
    pub decoy2_enc: [u8; SECTION_SIZE],
}

impl Default for DataBody {
    fn default() -> Self {
        Self {
            audio_enc: [0u8; SECTION_SIZE],
            log_enc: [0u8; SECTION_SIZE],
            decoy1_enc: [0u8; SECTION_SIZE],
            decoy2_enc: [0u8; SECTION_SIZE],
        }
    }
}

pub struct DataRelayHeader {
    pub timestamp_utc: u64,
    pub payload_hash: [u8; 32],
    pub relay_path: Vec<RelayPathEntry, 8>,
}

pub struct DataPacket {
    pub header: DataRelayHeader,
    pub body: DataBody,
}

impl DataPacket {
    pub fn calc_hash(&self) -> [u8; 32] {
        let mut h = Hasher::new();
        h.update(&self.header.timestamp_utc.to_be_bytes());
        for entry in self.header.relay_path.iter() {
            h.update(&entry.aircraft_id);
            h.update(&entry.hop_number.to_be_bytes());
        }
        h.update(&self.body.audio_enc);
        h.update(&self.body.log_enc);
        h.update(&self.body.decoy1_enc);
        h.update(&self.body.decoy2_enc);
        *h.finalize().as_bytes()
    }
}
