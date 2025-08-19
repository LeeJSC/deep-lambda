/// Hardware abstraction for radio transceivers.
pub trait Radio {
    /// Send raw bytes over the air.
    fn send(&mut self, buf: &[u8]);
    /// Receive bytes into the buffer, returning number of bytes received.
    fn recv(&mut self, buf: &mut [u8]) -> usize;
}

/// Dummy radio used for compilation/testing.
pub struct DummyRadio;

impl Radio for DummyRadio {
    fn send(&mut self, _buf: &[u8]) {}
    fn recv(&mut self, _buf: &mut [u8]) -> usize { 0 }
}
