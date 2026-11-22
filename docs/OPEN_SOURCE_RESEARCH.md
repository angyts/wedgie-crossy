# Open-source Crossing Game Research

Date: 2026-11-22
Project: angyts/wedgie-crossy
Status: curated source-code review, not an exhaustive survey of all GitHub projects. No third-party code or assets copied.

## Objective

Identify useful ideas from publicly available Crossy Road-style and Frogger-style Python games, then adapt the ideas to Wedgie's MicroPython, 240x240 screen, 16-color framebuffer, bounded RAM, deterministic procedural world generation, and time-aware fairness requirements.

## Projects inspected

### 1. TbrosN/crossy-road
https://github.com/TbrosN/crossy-road

Source reviewed: src/crossy/game.py, terrain.py, obstacles.py, player.py, config.py, and README.md.

Most directly relevant gameplay reference. Separates GameState, Player, TerrainManager, and ObstacleManager. Includes grass, roads, rivers, trains, trees, vehicles with differing widths, moving logs, train warning state, camera pressure, score based on furthest progress, and high-score persistence.

Useful ideas: separation of gameplay concerns; traffic width and speed variants; river log support and drift; train warning periods; difficulty changes to terrain mixture and lane clusters; safe grass breaks between hazardous sections.

Limitations: terrain is generated as a fixed 100-row world, not an endless sliding window; Python random and floating-point coordinates are used; obstacles are represented as individual Python objects; independent random generation does not establish time-feasible paths through adjacent sections. Train initialization may immediately place a train, which needs extra entry-state validation. Adapt concepts, not the desktop implementation.

### 2. ejaysrngy/Crossy-Road-clone-Python
https://github.com/ejaysrngy/Crossy-Road-clone-Python

Source reviewed: README.md, cars.py, main.py, player.py.

A Turtle-based road-crossing game with multiple lanes, varying vehicle lengths and speeds, and progressively faster gameplay.

Useful ideas: parameterize lanes independently by speed, direction, vehicle width and spacing. Keep lane motion separately testable.

Limitations: hardcoded lanes, per-car Turtle objects, frame-sleep-driven motion, point-distance collisions, finite levels and no section-join feasibility analysis. Do not port object allocation or rendering approach to RP2040.

### 3. xanman42/crossy-road-clone-with-turtles
https://github.com/xanman42/crossy-road-clone-with-turtles

Source reviewed: main.py, car_manager.py.

Minimal Turtle crossing game with a CarManager handling movement, spawn, restart and speed increase.

Useful ideas: a narrow manager interface makes spawning and reset behavior easy to test.

Limitations: frame-dependent random spawning, dynamically growing Turtle objects, no speed cap and no fairness validation. Convert spawn rates to explicit time/space parameters and cap difficulty.

### 4. unix2dossss/Boxxy-Roads
https://github.com/unix2dossss/Boxxy-Roads

Source reviewed: README.md, obstacles.py, main.py.

Turtle crossing game with dynamic obstacle spawning, cleanup of old obstacles and NEAT-based multi-agent evaluation.

Useful ideas: host-side automated agents can probe edge cases and stress gameplay; relative hazard position is useful for adversarial test policies; obsolete hazards should be removed.

Limitations: NEAT and Turtle are inappropriate on constrained Wedgie hardware. An agent's success is not proof of reachability, and nearest-obstacle heuristics may miss trains or unsafe joins. Use deterministic offline validation as the correctness gate; optional agents are exploratory tools.

### 5. clawdbotatg/wedgie-starter
https://github.com/clawdbotatg/wedgie-starter

Source reviewed: dodge/dodge.py, hilo/hilo.py, wedgie.json, README.md.

Primary implementation reference for the actual platform. Dodge demonstrates prebuilt 4-bit sprites, fixed loop timing, reused obstacle records, UI, and persistent best score. Hi-Lo demonstrates wedgie.rand_below(), rand_source(), and event-driven input.

Important caveat: Dodge's comments about asynchronous DMA are outdated relative to current firmware. Current lcd.show_start() is synchronous and show_wait() is a no-op. Follow the audited firmware, not old optimization comments.

### 6. clawdbotatg/wedgie-dev
https://github.com/clawdbotatg/wedgie-dev

Source reviewed in the platform audit: public/code.md, docs/APPS.md, firmware/lcd.py, firmware/save.py, firmware/wedgie.py.

Authoritative reference for app manifests, firmware APIs, display and palette constraints, random source, persistence, USB servicing, emulation, and installation. See docs/PLATFORM_CODING_GUIDE.md and docs/HARDWARE_AUDIT.md for full platform findings.

## Comparative findings

| Concern | Reusable idea | Wedgie Crossy implementation |
| --- | --- | --- |
| Architecture | Separate state, terrain, hazards and player | Pure host-testable core plus thin Wedgie adapter |
| Terrain | Weighted clusters and grass breaks | Validated parametric sections with guaranteed resting opportunities |
| Roads | Vary vehicle lengths, speed, direction and spacing | Compact periodic lane parameters, no persistent car objects |
| Rivers | Moving logs carry the player | Fixed-point support, drift and edge-death checks |
| Railways | Warning before trains arrive | Phase-aware warning, arrival and swept collision rules |
| Scoring | Furthest forward row | Monotonic maximum progress |
| Difficulty | Mix terrain, speed, density and length | Smooth increase through score 200, then cap |
| Memory | Clean old obstacles; reuse records | Fixed-size sliding row and hazard window |
| Randomness | Hardware randomness in starter | Fresh hardware seed, deterministic PRNG thereafter |
| Validation | Existing clones do not establish section-join safety | Offline time-expanded reachability validator |
| Testing | Automated agent simulations | Seeded fixtures, randomized invariants, million-row stress |
| Graphics | 4-bit sprites and palette | Prebuilt pixel art, dirty-region updates, device profiling |

## Design requirements to carry forward

1. Define compact row/section schemas: terrain kind, absolute row index, pattern family, speed, spacing, obstacle length, direction, phase, difficulty band and entry/exit compatibility.
2. Define the deterministic PRNG algorithm and version; a recorded seed must reproduce the same generated world regardless of frame timing.
3. Evaluate vehicle and log positions from periodic integer/fixed-point equations with off-screen margins and correct negative-direction wrap.
4. Keep at most a bounded window of active rows and hazards. Never accumulate one object per previously visited row.
5. Model log support continuously across a simulation step; carry the player with the platform and test edge drift.
6. Model train warning start, train arrival, width, speed, period and phase. Test warning visibility and reaction allowances.
7. Build an offline time-aware validator over row, column/horizontal offset, time tick, support state and entry phase. Check moving hazards, section joins and camera pressure. Explicitly state the validation horizon and assumptions.
8. Use swept collision or bounded substeps so fast vehicles and trains cannot tunnel past the player.
9. Cap risk parameters at the locked difficulty ceiling; enforce safe resting opportunities across section boundaries.
10. Test seeded replay, impossible joins, adversarial hazard phases, blocked movement, monotonic scoring, river drift, train warnings, restart, persistence and one million uninterrupted generated rows.

## Licensing and reuse policy

Public GitHub access does not automatically grant permission to copy source code or assets. This review extracts general design concepts only; no third-party code was copied. Boxxy-Roads README states MIT, and Wedgie starter/dev identify as MIT. Licenses for TbrosN, ejaysrngy and xanman42 were not verified during this review. Before copying any actual code, inspect the license at a pinned revision, check compatibility, preserve required notices and attribution. Use original pixel-art assets.

## Recommended priority

**Adopt:** modular game core, width-aware hazards, moving log support, warned trains, furthest-row scoring, validated terrain clusters, deterministic seed, fixed-size world window, host-side fairness validation.

**Avoid:** finite static maps, uncontrolled global random state, unbounded obstacle objects, frame-rate-dependent spawn probabilities, uncapped speed escalation, desktop Turtle/Pygame dependencies, and using an AI agent as proof of solvability.

**Defer:** neural-network agents, elaborate graphics pipelines and unlock systems until v0.1 gameplay and hardware acceptance are complete.

## Research limitations and next steps

This is a selected source-code sample, not a comprehensive audit of every open-source crossing game. None of the inspected games demonstrated the full time-aware, cross-section reachability guarantee required by the locked specification. Further targeted research into time-expanded path planning and formal procedural-content validation may improve the validator.

Next engineering milestone: implement a host-only pattern schema, deterministic PRNG and time-aware validator, with known-valid and known-impossible multi-lane fixtures. Follow docs/SPEC.md, docs/PLATFORM_CODING_GUIDE.md and docs/HARDWARE_AUDIT.md.
