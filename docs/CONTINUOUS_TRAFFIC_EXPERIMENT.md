# Continuous traffic rendering — experimental hardware checkpoint

Commit: e19ce7b (initial runtime integration). Branch: main.

## Changes
- `traffic_motion.py` contains integer interpolation, wrapped-coordinate and dirty-span helpers, with host unit tests.
- `crossy.py` enables `SMOOTH_TRAFFIC` and introduces `SMOOTH_FRAME_MS = 40`.
- `render_road_motion` redraws eligible road rows between traffic ticks using `lcd.show_rect(0, y, 240, 20)`. It rebuilds road markings and clips cars crossing the display seam.
- Cosmetic updates are skipped when the input queue is nonempty or the next traffic tick is imminent. The simulation and collision masks remain tile-based.

## Known limitations and important cautions
- **Not hardware verified.** Host tests have not been executed for this commit; the user must verify the actual device.
- The player's current road lane is intentionally excluded from interpolation. Thus visual smoothness is incomplete.
- This is not swept collision detection and must not be described as such.
- A row-wide 240x20 flush per changed road lane may still overload SPI when many lanes are visible. The 40ms gate limits attempts but does not guarantee 25 FPS.
- The previous preview path remains in the traffic-tick handler and may add redundant transfers. Consider disabling it after measuring the new path.
- Partial redraws share the LCD framebuffer with other draw paths. Verify that moving the player, pause/resume, and camera scrolling do not produce stale road sprites.
- Existing tests that assert older constant values or preview timing may need updates. Run the full suite before treating this as a stable build.

## Physical acceptance checklist
1. Observe car motion on roads other than the chicken's current lane; compare against previous tile jumps.
2. Hold the joystick and test short taps while several roads are visible.
3. Watch for tearing, flickering, stale cars, road-stripe corruption, or stalls.
4. Check both travel directions and cars crossing left/right screen edges.
5. Test pause/resume, death/restart, scrolling and changing difficulty.
6. Measure real frame time and heap use with diagnostics; do not infer FPS from the nominal 40ms gate.

## Rollback
The previous gameplay commit before the renderer change is `99fccb27b1f796e9da11f47bfedd94f37927e4f0`. Revert the renderer commit `e19ce7b61d2b3bcb5212407f13d2092c31d51c62` if hardware performance regresses. For an immediate temporary local fallback, set `SMOOTH_TRAFFIC = False` in `crossy.py` and reinstall.

## Next batch
- Run and repair full host tests.
- Avoid repeated whole-lane redraws where possible; compute seam-aware dirty rectangles.
- Make animation and collision timing consistent, including swept occupancy and moving onto roads.
- Verify input latency and smoothness on physical Wedgie before expanding to logs.
