# Replayable route witnesses (offline)

find_witness searches for one successful sequence of (dy,dx) moves,
preserving absolute hazard ticks and camera state. replay_witness
executes that sequence through the same step_fp transition without
running search. The returned positions and tick count make failures
reproducible and support future runtime-parity tests.

The search remains bounded and provisional. A witness proves only
existence under the current simulation rules, not human reaction
fairness, real-time pacing or runtime equivalence. All outputs
explicitly remain deployable=false. ApprovedWorld stays grass-only.
