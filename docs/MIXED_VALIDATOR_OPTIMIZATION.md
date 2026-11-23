# Mixed route search optimization — 2026-11-23

## Why
The first 18-case benchmark completed in 6.031 seconds (~2.98 cases/s). At that measured rate, the original 12,000-case sweep would take about 67 minutes. The previous BFS copied a complete path tuple for every explored edge and recomputed procedural masks repeatedly.

## Changes
- Joined-section BFS now stores a set of (row, column) states per tick and one predecessor link per visited state. It reconstructs a witness only after reaching the goal.
- Per-search caches store terrain kinds by row and occupancy masks by (row, phase).
- Deterministic state ordering supports reproducible witness output.
- Added a regression test comparing optimized reachability against an independent small reference frontier across multiple seeds, blocks and starting phases.
- Live game code, Wedgie manifest and firmware remain unchanged.

## Correctness and performance gates
This change has **not** been executed or benchmarked in the assistant environment. Run:
```bash
python -m unittest discover -s tests -v
python tools/sweep_mixed_terrain.py --seeds 3 --phases 2 --ticks 36
```
Compare against the prior benchmark: 18/18 witnesses in 6.031 seconds. A different witness path may be equally valid; the new test checks reachability and replays successful paths. If those checks pass, increase workload incrementally while observing ETA. Do not immediately rerun 1,000 seeds.

## Limitations
Still a simplified one-input-per-tick model, not a proof of human reaction-time fairness or all-seed reachability. Caches are per search, not global, to keep memory bounded. Mixed terrain remains disabled on device.

## Rollback
Revert `cd46ee4` and `1cc1112` if tests fail or performance regresses. Existing live gameplay is unchanged.
