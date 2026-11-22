# Wedgie runtime foundation

The `wedgie-runtime` Rust crate is `no_std`, uses no allocator,
and introduces fixed-size player state, movement, tree blocking,
and deterministic camera pressure. It deliberately supports grass only.

Run locally:
```bash
cd wedgie-runtime && cargo test
cargo check --manifest-path wedgie-runtime/Cargo.toml --lib
```

This is a portable library, not yet a Wedgie firmware build. There is
no device input, framebuffer, display driver, or hazard physics yet.
The Rust camera rule mirrors the Python reference formula, but full
cross-language parity fixtures have not yet been implemented.
Offline fairness search remains on the host. No road admission.
