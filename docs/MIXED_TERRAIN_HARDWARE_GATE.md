# Mixed terrain hardware gate — 2026-11-23

## Implementation
The live generator now has a single `section(seed, row)` entry point. Its `MIXED_TERRAIN` switch defaults to `False`, preserving the previously accepted terrain. When explicitly enabled, selected interior road lanes become logs using the deterministic candidate planner. All live callers of `section()`, including drawing and collision masks, use the same type.

The candidate function uses `_base_section()` to avoid recursive calls. Existing grass buffers and the first/last road lane of each section are preserved. The offline validator uses the same deterministic parameters for proposed log lanes.

## Regression gate
`tests/test_mixed_live_parity.py` checks the default-off behavior, existing sections, enabled candidate kinds, and phase-specific road/log occupancy parity against the offline validator.

The assistant has **not** run the test suite or tested the switch on a physical Wedgie. The user's prior 1,200/1,200 witness sweep is evidence of feasibility under a simplified one-action-per-tick model, not proof of human fairness.

## Activation remains blocked
Do not enable `MIXED_TERRAIN` until:
- All host tests pass.
- Reaction-time, joystick timing, and moving-support behavior are modeled and checked.
- Hardware trial verifies dense-log FPS, input responsiveness, cold boot, and scoreboard integrity.

## Rollback
Revert commits `902d513` and `7a2728b` to remove the switch and parity test. With the switch off, the intended live terrain behavior is unchanged.
