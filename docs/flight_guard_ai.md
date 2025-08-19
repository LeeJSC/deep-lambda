# Flight Guard AI Mesh Protocol

## Overview

Flight Guard AI defines a secure inter-aircraft mesh network that allows aircraft to relay
telemetry and voice data when satellite links are unavailable. Every aircraft runs the
same software stack and can act as an emitter or receiver.

## Hardware Requirements

- **CPU**: ARM Cortex-A53/A72 or comparable RISC-V (1–2 GHz) with NEON extensions
- **Memory**: 2 GB or more of ECC RAM
- **Security**: Hardware TPM or HSM for key storage, optional crypto acceleration
- **Networking**: Redundant Ethernet or avionics-grade Wi-Fi/mesh radio
- **RTOS**: seL4, QNX, or RTEMS with Rust/Python cross-compilation support

## Module Functionality

| Module          | Purpose |
|-----------------|---------|
| `identity.py`   | Loads keys, holds certificates, and signs messages |
| `handshake.py`  | Establishes session keys via Noise/DTLS handshakes |
| `crypto.py`     | Provides AEAD encryption/decryption helpers |
| `packets.py`    | Defines ping, pong, data relay, and ack packet structures |
| `relay.py`      | Maintains neighbor state and forwards packets |
| `node.py`       | Application entry point tying all pieces together |


## Security Foundations

Flight Guard AI leverages well-vetted open source cryptographic
libraries instead of custom algorithms. Identities are represented by
Ed25519 certificates kept in TPM or HSM hardware.  Handshakes follow the
Noise IK pattern (as popularized by WireGuard) using X25519 key
exchange.  ChaCha20‑Poly1305 provides authenticated encryption for the
four fixed-size packet sections while BLAKE2s hashes uniquely identify
payloads.  Certificates are short‑lived and checked against revocation
lists before accepting a peer.


## Protocol Highlights

1. **Ping/Pong**: Aircraft announce presence with signed pings.
2. **Wellness Check**: A receiving aircraft verifies the signature and responds with a pong.
3. **Data Relay**: When satellite connectivity is lost, packets with four encrypted sections
   (audio, data log, and two decoys) are relayed through the mesh. Each header includes a
   unique payload hash and timestamp.
4. **Acknowledgment**: Each relay returns an ACK containing the payload hash and the
   measured time-of-flight in milliseconds.
5. **Adaptive Routing**: If time-of-flight increases, nodes initiate ping sweeps to locate
   nearer neighbors while continuing transmission.

All timestamps are expressed in UTC to keep logs consistent.
