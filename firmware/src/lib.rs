#![no_std]

mod crypto;
mod handshake;
mod identity;
mod node;
mod packets;
mod radio;

use core::panic::PanicInfo;
use radio::DummyRadio;
use rand_chacha::ChaCha8Rng;
use rand_core::SeedableRng;

#[no_mangle]
pub extern "C" fn main() -> ! {
    let radio = DummyRadio;
    let rng = ChaCha8Rng::seed_from_u64(0x1234_5678);
    let mut node = node::Node::new(radio, rng);
    // Main loop would process incoming packets; here we just send a dummy packet
    loop {
        node.send_dummy();
    }
}

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}
