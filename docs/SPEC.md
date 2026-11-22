# Wedgie Crossy — Specification v0.1

Status: gameplay and world-generation design locked; implementation not started.

## Goal
An endless, colorful, top-down pixel-art crossing game for Wedgie (target display 240x240, 20px tiles, 12x12 visible grid), inspired by classic road-crossing arcade games. Original artwork and proper attribution for any reused open-source code.

## Gameplay
- Four-directional, one-tile-per-press movement; trees block movement.
- Score equals furthest forward row reached; moving back or revisiting rows never awards points.
- Grass, roads with cars/trucks, rivers with moving supporting logs, and railways with warned trains are included in v0.1.
- Vehicle/train collisions, unsupported water, drifting off-screen, and falling behind the camera cause game over.
- Classic pace: camera follows progress; an initial proposed 5-second inactivity grace period precedes a rising danger boundary. Only reaching a new furthest row resets the timer.
- Title, gameplay, game-over/restart states; persistent high score written only when improved.
- Difficulty grows through score 200 then caps, preserving endless variety without unbounded speed or density.

## Parametric Pattern Engine — LOCKED
Store compact mathematical templates and parameters, not large pregenerated maps or individual persistent obstacle objects.
- Hardware TRNG provides a fresh seed each run; a small deterministic PRNG generates patterns. Fixed seeds reproduce runs in tests.
- Pattern families: grass (tree layout/corridors), roads (speed/spacing/direction/length/phase), rivers (log length/gaps/drift/phase), railways (train period/length/speed/warning), and compatible multi-lane sections.
- Example repeating traffic position: x_i(t) = (x0 + i*S + v*t) mod L (with suitable off-screen margins).
- Use integer/fixed-point math where practical; store compact parameters and derive positions as needed.
- Parameter ranges and section entry/exit compatibility must be validated offline. Individual safe lanes do NOT imply safe combinations.
- On device: inexpensive selection from validated pattern families; no exhaustive runtime pathfinding.
- Use a bounded sliding window of active rows and hazards; discard rows behind the camera. Memory use must not grow with distance.
- Fairness contract: generated sections should provide at least one continuous, time-feasible route from a defined valid entry state, with human reaction allowances. This does not guarantee survival from arbitrary player mistakes. Validation evidence is conditional on tested parameter ranges and timing assumptions.

## Proposed tuning values (verify on device)
- Target 20–30 FPS; fixed simulation timestep with swept collision for fast hazards.
- At least three initial safe grass rows; no more than five consecutive dangerous lanes without a safe resting opportunity.
- Proposed minimum 1-second crossing opportunity, 1.5-second train warning, 300ms reaction allowance.
- Proposed active window ~20–30 rows; exact bound to be measured.
- All values above are provisional engineering targets, not measured guarantees.

## Testing and acceptance
- Desktop unittest and GitHub Actions for movement, scoring, hazards, log drift, train warnings, collision tunneling, camera, persistence, seeded reproducibility, restart, and generator invariants.
- Offline time-aware validation of multi-lane sections and their joins; test across difficulty bands and permitted parameter combinations.
- Stress test at least 1,000,000 generated rows without resetting: bounded active rows/hazards, no runaway memory growth, large coordinate correctness, stable per-row generation cost, continued terrain diversity and difficulty cap.
- Randomized simulated games and 100,000-spawn tests; validate reachability assumptions and human reaction margins.
- Hardware acceptance: verify actual Wedgie input/display/TRNG/storage APIs, frame timing, memory footprint, and long-running stability.
- A million-row test is evidence, not a mathematical proof of infinity or universal reachability.

## Porting and licensing
Audit candidate permissively licensed open-source Python implementations before reuse. Reuse compatible logic, replace desktop graphics/input with Wedgie adapters, preserve upstream license/attribution. Inspect the existing Wedgie Snake project for verified hardware interfaces and test patterns.

No game code is authorized by this specification alone.
