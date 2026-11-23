# Mixed-terrain time-aware validator — first implementation

## Scope
Added `tools/crossy_mixed_validator.py`, an **offline-only** bounded breadth-first search of proposed mixed road/log layouts. It is not included in `wedgie.json` and does not run on the RP2040. Live terrain and the accepted game remain unchanged.

## Model
- State is (absolute row, column, traffic phase); each transition consumes one tick.
- Actions: wait, left, right, up, down. No diagonals.
- Road occupancy follows deterministic origins, direction and period.
- Mixed log candidates use the existing log origin, length, direction and period calculations.
- Water requires support before and after the tick. Moving logs carry the chicken one cell on movement ticks, with off-screen death.
- Road collisions are checked at both endpoints. Grass tree masks block occupancy.
- A route starts at center column of the grass row before a section and must reach the grass row after the 12-row block.
- `validate(seed, block, phases, max_ticks)` counts start phases with a witness route.

## Limitations — do not activate candidates yet
This is a **feasibility prototype**, not a certification of human fairness or an exhaustive proof:
- One action per traffic tick is a simplifying assumption; the real joystick can register presses between ticks.
- No reaction-time, input latency, display FPS or timing-jitter budget.
- No explicit swept sub-tile collision for cars.
- The route starts from one canonical entry column; not all reachable entry states are explored.
- It does not yet certify joins between consecutive blocks or a global path through the full game.
- No exhaustive seed/phase/difficulty sweep or performance budget has been completed.
- The validator and its tests have been committed but not executed in this environment.

## Next acceptance gates
1. Run `python -m unittest discover -s tests -v` and repair failures.
2. Add a time-expanded section-join validator, multiple entry states and conservative timing assumptions.
3. Measure witness coverage over many seeds and difficulty bands, including known seeds 0x3F564588 and 0x0676964C.
4. Activate only certified pattern families via an explicit switch, then hardware-test input latency, memory, smooth traffic and cold boots.

## Rollback
These commits add offline files only. Revert `e19f626` and `c4f14e2` if needed; the live hardware baseline is unaffected.
