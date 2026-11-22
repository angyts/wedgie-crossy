# Shared fixed-point reachability prototype

The host-only `validate_fp` now calls `simulation_fp.step_fp` for every
candidate transition. It therefore shares the grass, road and river
movement/collision rules instead of duplicating river support logic.

The validator is NOT a fairness certificate. It tests a finite horizon,
selected entry phases and a simplified instantaneous movement model.
Railways, camera pursuit, complete phase coverage and section exit-state
compatibility remain open. Generated terrain is still uncertified.
