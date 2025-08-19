# Flight Guard AI Hardware & Firmware Notes

This document outlines how the mesh protocol can be deployed on
physical avionics hardware and whether a custom chip is required.

## Hardware Platform

* **Processor**: ARM Cortex-M7/A53 or comparable RISC-V core.
* **Memory**: \>= 2 MB flash, 512 KB RAM for firmware and buffers.
* **Crypto**: Prefer MCUs with AES/ChaCha accelerators and a TPM/TEE
  for secure key storage.
* **Radio**: Dual-redundant Ethernet, Wi-Fi 6, or specialized
  mesh-capable transceiver.

Off-the-shelf safety-certified modules (e.g., NXP i.MX, STM32H7) are
recommended. A custom ASIC is unnecessary unless size, power, or
certification constraints demand it. Using proven components shortens
certification time and leverages existing toolchains.

## Firmware Strategy

Firmware is written in `no_std` Rust for memory safety and low
latency. The `firmware` crate implements key management, X25519
handshakes, ChaCha20‑Poly1305 encryption, and fixed-size relay packets
that mirror the Python reference implementation. The `radio` module
abstracts the transceiver so the same code runs on different avionics
HALs.

Key points:

1. **Secure Boot**: Bootloader validates firmware signature before
   execution.
2. **Key Provisioning**: Device identity keys and certificates are
   loaded via maintenance port into TPM/secure element.
3. **Updates**: New firmware delivered over signed image, verified on
   device.
4. **Testing**: Hardware-in-the-loop simulations validate radio timing
   and mesh behavior before flight.

## Custom Chip?

A custom chip is generally **not** required. Leveraging existing
flight-certified MCUs with hardware crypto and secure boot features is
more practical and reduces risk. A bespoke chip might be considered for
future revisions if integration, power, or export controls make it
necessary.
