# Wedgie Crossy — Development Handoff (2026-11-22)

## Verified repository state
- Canonical game repository: `angyts/wedgie-crossy`, default branch `main`.
- Current specification: `docs/SPEC.md`, committed in `a6542dbf539259eceb6cf395b100219e529bb81c`.
- Development handoff: `docs/DEVELOPMENT_HANDOFF.md`.
- Hardware audit: `docs/HARDWARE_AUDIT.md`, committed in `7ba705834e8b3bed0db21cc0946c1f8286aa4027`.
- Specification explicitly states that implementation has not started; do not claim playable code or completed tests.
- Reference repositories: `angyts/wedgie-snake-game` for existing game conventions, `clawdbotatg/wedgie-starter` for complete app/game patterns, and `clawdbotatg/wedgie-dev` for firmware APIs. These are references, not the Crossy game repository.

## Locked product decisions
- v0.1: colorful pixel art, classic pace, grass/roads/rivers/railways.
- Four-direction, one-tile-per-press movement; furthest-forward-row scoring; persistent best score.
- Fresh hardware-backed random seed per run, then deterministic PRNG from the seed for reproducible generation.
- Compact parameterized patterns, fixed-point/integer simulation where practical, bounded sliding active window.
- Difficulty increases until score 200, then caps.
- Offline, time-aware validation of multi-lane patterns **and joins** under explicit reaction and crossing assumptions; runtime only selects validated families.
- Tests include million-row generation, bounded memory, collision tunneling, restart, storage, difficulty, and seeded replay.
- Initial timing/memory/viewport numbers in SPEC are provisional until measured on actual hardware.

## Verified Wedgie platform findings
See `docs/HARDWARE_AUDIT.md` for source links and details. Key implementation constraints:
- 240x240 display; joystick directions/press plus A/B/X/Y.
- Current framebuffer is 4-bit GS4_HMSB (~28.1 KiB), not an RGB565 framebuffer. Palette has 16 colors.
- Current `lcd.show_start()` calls synchronous `show()`; `lcd.show_wait()` is a no-op. Treat old starter comments about asynchronous DMA overlap as outdated compatibility guidance.
- Prefer dirty-region pushes via `lcd.show(y0, y1)` / `lcd.show_rect(...)`; profile actual frame costs on the physical board.
- Use `Keys().pressed()` for one-tile edge-triggered input; `Keys().held()` exists for continuous controls. Sleep briefly each loop so firmware USB service gets time.
- `wedgie.rand_below(n)` gives unbiased random integers; `wedgie.rand_source()` reports chip/fallback source. Seed once from hardware randomness then use deterministic PRNG for every generator choice.
- `save.load/store/delete` is per-app persistence. Store new high score only, not every frame.
- Package as a root `wedgie.json` plus app files, with `entry: "run"`. The main module basename and declared asset names must obey Wedgie's app naming rules.
- Use built-in `ui` for title/game-over UI. Emulator is not proof of physical RAM/speed; virtual Wedgie is closer but real hardware profiling remains required.
- Firmware source audited at v0.3.91; choose Crossy's `fw` floor from exact APIs used and check user's installed firmware.

## Engineering clarifications / risks
1. Hardware TRNG is for seeding, not for every world-generation decision: seed must be recordable so a failure can be replayed.
2. A valid route from one specified entry state does not mean every player position is recoverable. Validator must define entry states, temporal phase assumptions, moving platforms, and transition timing.
3. Independently safe lanes may compose into impossible sections. Validate cross-lane timing and section boundaries, including trains, logs, and camera pressure.
4. Bound memory by counting live rows and hazard parameter records, not by estimating the number of world rows. Long-running tests must check coordinate overflow and periodic phase arithmetic.
5. Use swept collision or equivalent substep handling for fast trains/vehicles so they cannot skip over the player between frames.
6. Difficulty cap must bound speeds, densities, and warning windows without eliminating variety or safe resting opportunities.
7. A 1,000,000-row stress test is empirical evidence, not proof of infinity or universal solvability.
8. Do not assume full-screen rendering at target FPS; the current synchronous display path makes partial rendering and measured profiling important.
9. The 130–150 KB free-RAM figure in platform guidance is an observed guide, not a hard guarantee; measure actual peak heap on the user's board and firmware.

## Next work (not yet implemented)
1. Build host-only pattern schema, deterministic PRNG wrapper, and parameter validation.
2. Specify pattern compatibility contract and deterministic time-aware offline validator, with pass/fail fixtures for impossible joins.
3. Add deterministic tests for valid/invalid road, river, railway and mixed-section transitions; phase timing; player reaction windows; camera-pressure assumptions.
4. Run million-row stress tests for bounded memory, arithmetic and reproducibility.
5. Add thin Wedgie adapter (`LCD`, `Keys`, `save`), fixed-timestep simulation, compact pixel-art renderer and dirty-region pushes.
6. Test in `wedgie.dev/code`, then virtual Wedgie, then physical board; record FPS, free heap, frame-time distribution and sustained stability.

## Handoff rule
Continue development in `angyts/wedgie-crossy` on `main` unless the user changes direction. Keep the locked `docs/SPEC.md` as source of truth. Clearly separate source-audited facts, provisional design targets, host test results, and physical-hardware measurements.
