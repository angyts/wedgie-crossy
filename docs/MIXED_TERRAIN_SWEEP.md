# Mixed terrain feasibility sweep

## New offline tooling
`tools/sweep_mixed_terrain.py` runs deterministic, phase-aware continuous-route searches across early, middle and late terrain blocks. It includes the two previously problematic hardware seeds before testing a reproducible seed stream.

Example:
```bash
python tools/sweep_mixed_terrain.py --seeds 1000 --phases 4 --ticks 72 --blocks 2 --json reports/mixed_sweep.json
```

This command examines 12,000 cases (1,000 seeds × 3 bands × 4 phases), reporting witnesses, no-witness cases, all-phase-passing seed groups, elapsed time and bounded failure examples. It exits with code 2 if any case has no witness, intentionally making an unsafe or inconclusive sweep visible in CI.

## Critical limitations
- **No 12,000-case result has been measured or committed.** This commit provides the runner, not a successful validation report.
- A route witness under one-action-per-tick timing is not a guarantee of human playability.
- A no-witness result may reflect the 72-tick search limit or restricted entry state rather than a truly impossible route.
- The search does not model measured joystick reaction time, LCD lag, continuous swept collision or camera pressure.
- Passing a finite sample does not prove all 32-bit seeds safe.
- No mixed-terrain feature is enabled in `crossy.py` or `crossy_worldgen.section()`.

## Acceptance gates
1. Run full host unit tests and fix any failures.
2. Run the full sweep; archive JSON results and investigate every no-witness case.
3. Add conservative timing and joined-entry-state checks, then certify a bounded family.
4. Only then activate selected patterns and test cold boot, FPS, log responsiveness and traffic on the physical Wedgie.

## Rollback
Only offline tooling and tests changed. Revert `d96f1c1` and `993d73d` if necessary.
