# Cross-language parity fixtures

The camera vectors in `fixtures/camera_parity.csv` are executed by
both Python's `Camera` and the Rust `no_std` runtime camera.
Each row includes camera parameters, a sequence of player rows,
expected death decisions and exact camera boundaries for each tick.

This is a first parity gate, not full gameplay parity. Movement,
hazards, camera integration, display and actual Wedgie compilation
remain separate milestones. Rust uses `Vec` only inside its host-side
test harness, never in the device library. The approved generator
remains grass-only.
