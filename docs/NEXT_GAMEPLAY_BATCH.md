# Hardware baseline and next gameplay batch — 2026-11-23

## Accepted baseline
User reported satisfactory hardware behavior at commit `869406f`, after previous improvements to smooth road movement, log-row partial transfers, player dirty-row redraws, and cold-boot startup.

## This batch
- Three car sprite variants gain small distinguishing window/highlight details, inside their existing 20x20 tile footprint.
- Added `tests/test_hardware_baseline_regression.py` to guard application file namespace/manifest completeness, lazy runtime import, top HUD row protection, log partial transfers, and avoidance of blocking log-carry animation.
- No gameplay physics, collision masks, terrain generation, traffic cadence or persistence changed.

## Why mixed terrain is deferred
`docs/SPEC.md` requires time-aware reachability and section join compatibility. Existing experimental mixed terrain validators do not establish universal fairness. Do not enable unrestricted mixed terrain until a bounded certified family is validated.

## Verification
- GitHub source was inspected using the connected repository.
- Full host tests were **not executed**: the working container could not resolve github.com to clone the repository. The new regression checks are committed but unverified.
- Physical performance and memory must be checked before calling this batch accepted.

## Reproduction cases
- Smooth-car stability: seed `0x3F564588`, around row 36.
- Dense log performance and joystick input: seed `0x0676964C`, around row 43.
- Cold boot: unplug/replug and launch Crossy without running the debug command.

## Rollback
Revert cosmetic and test commits if they cause issues; previous hardware-accepted baseline: `869406f4d0e96d37d1b238ddee315ce35b31a072`.
