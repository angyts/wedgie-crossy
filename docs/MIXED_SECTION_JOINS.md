# Continuous mixed-section join validation

## New capabilities
`tools/crossy_mixed_validator.py` now provides:
- `joined_route(seed, first_block, block_count, start_phase, max_ticks, entry_columns)`: bounded multi-block BFS retaining the actual column and absolute traffic phase at every section join.
- `replay_joined_route(...)`: independently steps through a returned move sequence using the same transition rules.
- `validate_joins(...)`: counts starting phases with a continuous witness.

The search does not reset to the center column between blocks. It supports wait and four cardinal moves, moving-log carry and endpoint occupancy checks.

## Verification limitations
This is still **not a human-fairness certification**. One action per tick is a model assumption; real input timings differ. It lacks measured reaction allowances, swept pixel collision, camera pressure and hardware frame-time jitter. A bounded search that finds no witness is not a proof of impossibility.

The newly added tests were not run in the assistant environment. Do not enable mixed terrain on hardware yet.

## Next gate
Run all unit tests, then perform large seeded multi-block phase sweeps with explicit thresholds and record failures. Add realistic reaction-time and phase-dependent entry constraints. Only then consider activating a limited family behind a feature flag.

## Rollback
These changes affect offline tools and tests only. Revert commits `0ad6323` and `188705e` to undo them. The live gameplay baseline is unchanged.
