# Wedgie Crossy — Development Handoff (2026-11-22)

## Verified repository state
- Canonical game repository: `angyts/wedgie-crossy`, default branch `main`.
- Current specification: `docs/SPEC.md`, committed in `a6542dbf539259eceb6cf395b100219e529bb81c`.
- Specification explicitly states that implementation has not started; do not claim playable code or completed tests.
- Reference repositories: `angyts/wedgie-snake-game` for existing Wedgie game conventions and `clawdbotatg/wedgie-dev` for firmware APIs. These are references, not the Crossy game repository.

## Locked product decisions
- v0.1: colorful pixel art, classic pace, grass/roads/rivers/railways.
- Four-direction, one-tile-per-press movement; furthest-forward-row scoring; persistent best score.
- Fresh hardware randomness for run seeds, deterministic PRNG from the seed for reproducibility.
- Compact parameterized patterns, fixed-point/integer simulation where practical, bounded sliding active window.
- Difficulty increases until score 200, then caps.
- Offline, time-aware validation of multi-lane patterns **and joins** under explicit reaction and crossing assumptions; runtime only selects validated families.
- Tests include million-row generation, bounded memory, collision tunneling, restart, storage, difficulty, and seeded replay.
- Initial timing/memory/viewport numbers in SPEC are provisional until measured on actual hardware.

## Engineering clarifications / risks
1. Hardware TRNG is for seeding, not for every world-generation decision: seed must be recordable so a failure can be replayed.
2. A valid route from one specified entry state does not mean every player position is recoverable. Validator must define entry states, temporal phase assumptions, moving platforms, and transition timing.
3. Independently safe lanes may compose into impossible sections. Validate cross-lane timing and section boundaries, including trains, logs, and camera pressure.
4. Bound memory by counting live rows and hazard parameter records, not by estimating the number of world rows. Long-running tests must check coordinate overflow and periodic phase arithmetic.
5. Use swept collision or equivalent substep handling for fast trains/vehicles so they cannot skip over the player between frames.
6. Difficulty cap must bound speeds, densities, and warning windows without eliminating variety or safe resting opportunities.
7. A 1,000,000-row stress test is empirical evidence, not proof of infinity or universal solvability.

## Next work (not yet implemented)
1. Audit actual firmware input/display/TRNG/storage interfaces against the reference repositories; record signatures and version assumptions.
2. Specify parameter schemas, pattern compatibility contract, and a deterministic time-aware offline validator, with pass/fail fixtures for impossible joins.
3. Build host-only generator and tests before adding hardware rendering.
4. Add the Wedgie adapter, fixed-timestep game loop, renderer, save/restart flow, and on-device profiling.
5. Run CI and hardware acceptance; record actual FPS, RAM, and long-run stability.

## Handoff rule
Continue development in `angyts/wedgie-crossy` on `main` unless the user changes direction. Keep the locked `docs/SPEC.md` as source of truth. This handoff documents findings only; it does not authorize or represent game-code implementation.
