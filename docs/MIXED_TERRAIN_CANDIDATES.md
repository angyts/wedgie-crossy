# Mixed terrain — candidate design checkpoint

## Implemented
`crossy_worldgen.mixed_section_candidate(seed, row)` generates deterministic proposed road/log alternations within selected existing road sections. It preserves grass buffers, the section's first and last road lanes, and all existing live terrain. Added deterministic host tests.

**This is not enabled in gameplay.** The live `section()` function, terrain masks, log drift, collision and rendering remain unchanged.

## Why gated
The specification requires a continuous, time-feasible path with reaction allowances, not merely one safe tile per row. Road/log transitions introduce moving support and collision timing that must be evaluated together. Without an offline time-expanded validator, enabling the candidate would risk impossible sections.

## Validation needed
- Model phase-dependent occupancy, joystick hops, carrying, off-screen drift and road collisions.
- Check section entries/exits and grass-buffer joins across difficulty bands.
- Verify many seeds including 0x3F564588 and 0x0676964C.
- Check rendering cost and input latency on physical RP2040, especially dense log rows.
- Only after certification should a separate explicit switch activate mixed sections.

## Hardware baseline and rollback
The previously accepted game remains unchanged. Roll back candidate commits `1108089` and `8bae221` if needed; no reinstall required because the new function is never called by live gameplay.
