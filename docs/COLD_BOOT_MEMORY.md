# Cold-boot memory refactor — experimental checkpoint

## Reproduction
On firmware 0.3.91 / MicroPython 1.29.0, RP2040:
- Install succeeds and Crossy runs.
- Unplug/replug: app fails with `memory allocation failed, allocating 1336 bytes`.
- Running `python wedgie.py debug` then launching Crossy works.
- Debug snapshot reported 85,200 bytes free RAM and 856,064 bytes free flash. This is NOT the failing allocation's heap state.

Upstream `clawdbotatg/wedgie-dev/docs/PLAN-MEMORY.md` documents import-time compilation peaks on RP2040 and successful use of compatible .mpy files for another app. This suggests, but does not prove, the same root cause here.

## Changes
- Move `run()` into `crossy_runtime.py`; `crossy.py` exports a small lazy-loading entry wrapper.
- Include the runtime in `wedgie.json`.
- All app modules are named `crossy.py` or `crossy_*.py` to avoid collisions in the shared flash root.
- Preserve game logic and the hardware-accepted smooth-traffic code.

## Important limitations
- Splitting source does not guarantee a smaller total peak: both modules are still imported. The main module remains relatively large.
- Full host tests and physical cold-boot tests have not yet been run. Do not label this a verified fix.
- Import-time dependencies and test assumptions may require follow-up adjustments.
- If the error persists, the next approach is reducing per-module compile complexity further or evaluating compatible precompiled .mpy deployment, with care about stale .py files taking precedence.

## Test plan
1. Pull and install from main, then play briefly.
2. Disconnect power completely; reconnect and launch Crossy WITHOUT running debug.
3. Repeat at least five cold boots.
4. Confirm animation, joystick, log carry, score HUD, pause/restart.
5. Run `python -m unittest discover -s tests -v` on the host; fix any failures before calling the refactor stable.

## Rollback
Hardware-accepted baseline immediately before this refactor: `e1d7448fbd37f18164cffa00b0b446011cdadfea`.
Revert the runtime split commits if the game no longer launches, or restore the baseline files from that commit. Do not rewrite main history.
