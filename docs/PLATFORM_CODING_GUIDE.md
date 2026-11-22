# Wedgie Platform Coding Guide

**Status:** source-audited engineering reference for Wedgie Crossy. **Audit date:** 2026-11-22. **Upstream firmware source version:** `0.3.91` in `clawdbotatg/wedgie-dev/firmware/wedgie.py` at inspection time. This is **not** a promise that a particular physical board runs that version. Check installed firmware before deployment.

**Read first:** `docs/SPEC.md` (game requirements), `docs/HARDWARE_AUDIT.md` (source evidence), `docs/DEVELOPMENT_HANDOFF.md` (current work), then this guide. When this document disagrees with the upstream implementation for the actual firmware version, inspect upstream and record the change. Never silently assume stale examples are authoritative.

## 1. Architecture and boundaries

Wedgie is a Raspberry Pi Pico RP2040 or RP2350 running MicroPython and Wedgie firmware, with a 240×240 display, five-way joystick and A/B/X/Y keys. Apps run as MicroPython modules; **each app lives in its own repository**.

Crossy should separate:
- **Pure core:** PRNG, terrain/pattern schemas, fixed-point hazard trajectories, game state transitions, scoring, camera, collision, and window bookkeeping. No `lcd`, `machine`, `time`, `save`, or hardware imports at import time. Make host tests deterministic.
- **Offline validator:** time-aware feasibility search for multi-row patterns and joins, using explicit player move times, platform drift, hazard phases, reaction margins, and camera pressure. It is tooling, **not** an on-device hot-path dependency.
- **Wedgie adapter:** input, monotonic clock, random seed, display, UI, persistence, diagnostics. Keep device-specific logic narrow.
- **Assets:** prebuilt small 4-bit sprite/palette data; minimize runtime conversion and large allocations.

**Do not conflate**: pattern-family validity with every possible player's recoverability; emulator behavior with physical performance; one-million-row stress testing with proof of infinity.

## 2. App manifest and install layout

Root `wedgie.json` contains an `apps` array. Minimal Crossy shape (example, verify naming and firmware floor before shipping):

```json
{
  "apps": [
    {
      "mod": "crossy",
      "name": "Crossy",
      "about": "Endless pixel-art crossing game.",
      "files": ["crossy/crossy.py"],
      "entry": "run",
      "fw": "0.3.36",
      "label": "#22c452",
      "icon": [
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............"
      ]
    }
  ]
}
```

This is a **structural example**, not a production manifest or final icon. The `fw` floor above is an example for the broader UI kit, not a verified minimum for final Crossy. Validate with the upstream manifest validator `src/apps/appjson.mjs`.

Rules from upstream `public/code.md`:
- `mod`: 2–20 characters, lowercase ASCII letters/digits/underscore, starts with a letter; must not collide with firmware or MicroPython modules.
- Declared app files are installed at the device flash **root using their basenames**, even when repository paths are nested. Basenames must be `<mod>.py`/`.mpy` or begin `<mod>_`; permitted suffixes `.py`, `.mpy`, `.bin`, `.json`, `.txt`. Main module required.
- Up to 30 files and 256 KB per app according to guide. Verify against current validator for release.
- `entry: "run"`: firmware imports the module then invokes `run()`. Avoid running an endless loop during import.
- `name` is Title Case, at most 14 characters; `about` at most 140; `label` is a hex RGB color; `icon` has 12 strings of 12 characters from `.`, `k`, `w`, `g`, `r`, `y`, `b`, `s`.
- Only declare `chip`, `usb`, or `net` if truly needed. Crossy normally needs neither internet nor privileged secure-chip access; using firmware's random service is distinct from directly importing a chip driver.
- App installed from a public GitHub repository is unsigned/full-access; signed shelf distribution requires upstream review of a particular commit.

## 3. Screen and palette

Source: `firmware/lcd.py`.
- 240×240 pixels. Current firmware uses one shared `framebuf.GS4_HMSB` buffer of `240*240/2 = 28,800` bytes, plus a small RGB565 row staging buffer.
- 16 palette entries. `from lcd import LCD, Keys, color`; `lcd = LCD()`. `color(r,g,b)` returns **palette index**, not arbitrary RGB565. Use the actual current palette and test terrain contrast on the device.
- FrameBuffer C-backed primitives include `fill`, `fill_rect`, `rect`, `hline`, `vline`, `line`, `text`, `blit`, `scroll`. Avoid Python per-pixel loops in every frame.
- Precompute sprites once (e.g. `framebuf.FrameBuffer(bytearray((w*h+1)//2),w,h,framebuf.GS4_HMSB)`) and optional palette FrameBuffers. `blit` transparency/palette semantics should be verified against the target MicroPython build. Dodge demonstrates a working pattern.
- `lcd.tint(index,r,g,b)` temporarily changes one palette index until next `fill()`; reserve indices to prevent UI/terrain collisions. `lcd.art(...)` streams full-color RGB565 assets from flash at display time; avoid unless needed.
- `lcd.show(y0,y1)` pushes a full-width row band; `lcd.show_rect(x,y,w,h)` pushes a rectangle. Use dirty-region tracking; merge adjacent dirty areas when profitable. World scrolling may dirty most of the screen; measure whether tile/row redraw, scroll, or full push is cheaper.
- **Critical version caveat:** current `show_start()` calls synchronous `show()`; current `show_wait()` is a no-op. Dodge's DMA-overlap comments refer to an older implementation. Never assume DMA overlap or a free buffer while transmission occurs.
- Full-screen push and fill benchmarks in `public/code.md` are historical measurements and may differ on the current firmware. The 20–30 FPS Crossy target is provisional, not demonstrated.

## 4. Input and game controls

```python
from lcd import Keys
keys = Keys()
for key in keys.pressed():
    if key in ("up", "down", "left", "right"):
        # queue exactly one grid move; resolve in core logic
        pass
```

- `Keys().pressed()` reports new press edges; `Keys().held(name)` reports held state. Supported names: `up down left right press A B X Y`.
- `Keys(physical=True)` intentionally ignores virtual/USB-injected presses; do not use for normal game input or automated gameplay tests.
- Define simultaneous-direction arbitration and a maximum queued-input length explicitly; never allow an unbounded queue or multiple unintended steps per press.
- Use `time.ticks_ms()`, `time.ticks_diff()`, and `time.ticks_add()` for wrap-safe clock operations. Avoid comparing wrapped tick values by ordinary subtraction.
- Include `time.sleep_ms(max(1, remaining_ms))` or equivalent each loop; the firmware needs an opportunity to service USB. Do not busy-spin.
- Prefer fixed-timestep simulation, with bounded catch-up steps after a delayed frame; render frequency may differ from simulation frequency. Use a consistent order: read input → simulate hazards/player/collisions → update camera/window → render → push → sleep.

## 5. Randomness and deterministic replay

Source: `firmware/wedgie.py`, starter `hilo/hilo.py`.
- `from wedgie import rand_below, rand_source`; `rand_below(n)` uses rejection sampling to avoid modulo bias, for `n` up to 2**24 per current source.
- `rand_source()` may report ATECC608, OPTIGA Trust M, or an `os.urandom` fallback. Do not assert secure-chip entropy if firmware reports fallback.
- Obtain a fresh multiword seed once per game (e.g. combine two or more `rand_below(1<<24)` draws), then drive every world-generation choice from a documented deterministic PRNG. Do **not** use platform random calls during deterministic generation.
- Specify PRNG algorithm, word size, masking, overflow behavior, and serialization; fixed seeds must yield identical worlds in desktop tests and MicroPython. Test seed zero, high-bit values, and long sequences.
- Preserve seed and generator version in crash/debug reports; include difficulty and absolute row index. Avoid logging secrets (a game seed is not a secret).

## 6. Memory, allocations, and speed

The upstream guide reports approximately 130–150 KB of app heap on RP2040 **as an observed range**, not a guaranteed allocation budget.
- Preallocate active row descriptors, hazard parameter records, sprite buffers, scratch buffers and input queue. Reuse records via a bounded ring/window.
- Store **parameters**, not persistent per-obstacle objects or an ever-growing map. Evaluate periodic positions analytically from integer/fixed-point phase and time.
- Keep all hot-path state bounded independently of total distance. Test one million rows without a restart and assert max active rows/hazards/allocated bytes.
- Avoid string/bytes `+=` in loops, repeated list concatenation, and large per-frame temporary objects; these cause fragmentation. Use preallocated `bytearray` or join parts once outside the hot path.
- Minimize text formatting. Update score strings only on score changes. Avoid `gc.collect()` every frame; measure collection pauses and perform collection at controlled safe moments if necessary.
- Avoid floating-point drift for lane movement and phase. Bound multiplication and modulo arithmetic for large absolute row/time counters; use wrapped relative coordinates for active hazards if needed.
- Use `gc.mem_free()`, `gc.mem_alloc()`, and observed frame-time distributions where available. Log peak memory and worst/p95 frame time, not only averages.
- Preserve a meaningful free-memory margin on RP2040; measure under worst-case active terrain and transitions before deciding a fixed threshold.

## 7. Saves and persistent state

Source: `firmware/save.py`.
- `save.load("best", 0)` loads app-scoped persistent value; `save.store("best", best)` writes JSON-compatible value; `save.delete("best")` removes it.
- Firmware scopes saves under `/saves/<game>/`; do not manually write another app's save folder.
- Save only when the best score improves (normally on game-over), never every frame or every row.
- Handle `OSError` (flash full or I/O error) gracefully without crashing gameplay. Keep scores nonnegative and validate loaded types/ranges.
- Avoid storing the whole world or a large debug history on flash.

## 8. UI and accessibility

- Use firmware `ui` for title, game-over, questions, progress and status rather than inventing competing firmware chrome. `ui.page(lcd, title, lines, hint)` is demonstrated in starter Dodge.
- Follow `public/code.md` guidance: concise readable text, sufficient contrast, and firmware button-square hints (`{g}`, `{r}`, `{k}`) where supported; physical buttons have no letter legends.
- Preserve clear visual differentiation between safe grass, traffic, water/logs, railway, and train warning. Avoid color-only warnings: add flashing shape, outline, or movement cues.
- Reserve a safe score/UI region or draw UI over a contrasting background; avoid hiding hazards behind opaque UI.

## 9. Crossy simulation and fairness rules

Locked requirements live in `docs/SPEC.md`; implementation must follow them.
- Four-direction, one-tile-per-press movement; trees block. Score is maximum forward row reached, never decreases.
- Roads: cars/trucks. Rivers: supporting moving logs and drift. Railways: warned trains. Death on collision, unsupported water, off-screen drift, or falling behind camera.
- Camera advances with new furthest progress; inactivity grace and pressure timing must be explicit and testable.
- Difficulty increases through score 200 and caps. Cap **all** risk-affecting parameters, including speed, gaps, density, warning windows and section length.
- Each pattern family stores compact integer parameters, including speed, spacing, lengths, direction, and phase. Generation uses bounded difficulty-dependent ranges.
- **Do not rely on lane-by-lane safety.** Offline validator checks a time-feasible path through multi-lane sections and across section joins, including moving log support, moving hazards, reaction allowances, camera pressure, and valid entry states.
- Validation must state quantization (time step, player move duration), phase coverage, entry/exit contract, and assumptions. Finite testing cannot prove every arbitrary parameterization or arbitrary player position safe.
- For high-speed hazards, swept collision or bounded substeps prevent tunneling across player cells.
- Use a bounded active sliding window; regenerate/reuse descriptors only as needed, discard rows behind. Test coordinate overflow and deterministic replay across window shifts.

## 10. Testing matrix and acceptance

**Host unit tests (run in CI):**
- PRNG fixed-seed golden vectors, seed edge cases, reproducibility across runs.
- Terrain parameter bounds, pattern-family selection, difficulty-band caps, diverse terrain after long play.
- Movement/blocked tiles, scoring on new max row only, camera and inactivity pressure.
- Cars/trucks/train collision, swept tunneling, train warning timing.
- River support and moving-platform drift, edge-of-screen death.
- Save best only on improvement; failed save does not crash; restart resets run state.
- Validator pass/fail fixtures for valid/invalid sections **and joins**, including temporal phase adversaries.
- Randomized state-machine invariants and at least 100,000 generated spawns/fixtures as defined in SPEC.
- One-million-row uninterrupted stress: bounded active rows and hazards, no runaway allocations, stable row cost, correct large indices, variety and capped difficulty.

**Device tests:**
- Confirm installed firmware version and input mappings; validate actual LCD and palette.
- Run editor emulator, virtual RP2040, then physical RP2040/RP2350.
- Measure p50/p95/worst frame time, heap free/peak, flash footprint, input responsiveness, screen tearing, and long-play stability.
- Test after USB disconnect/reconnect, restart, best-score persistence, and low-flash conditions.
- Do not declare acceptance based on desktop tests or the unlimited-memory editor emulator alone.

Suggested commands (from upstream guide; actual device and permissions required):
```sh
# In wedgie-dev, optional virtual device:
node tools/emu.mjs

# On a connected Wedgie; requires appropriate USB access/confirmation:
python3 wedgie.py debug
python3 wedgie.py install .
python3 wedgie.py shot crossy.png
python3 wedgie.py press A
```

For editor iteration: https://wedgie.dev/code (WASD joystick; J/K/L/; buttons; R restart). For memory-realistic virtual firmware: https://wedgie.dev/virtual. Neither substitutes for physical frame timing.

## 11. Source priority and change management

**Priority:** (1) checked-in Crossy product requirements, (2) installed firmware source/API for the target version, (3) upstream current app guide and validator, (4) starter examples, (5) old benchmark comments. If an upstream source changes, update this guide and `docs/HARDWARE_AUDIT.md` with the precise observation and version/date; do not repeatedly re-audit unrelated code.

Before editing code, inspect existing repo state and tests. Make small, reviewable commits with clear messages. Never claim a test ran without a recorded command/result. Avoid modifying upstream repos. Avoid force-push. Keep dependency and license attribution when copying upstream code. The inspected upstream repos identify their license as MIT; retain notices for reused material.

**Useful upstream references:**
- https://github.com/clawdbotatg/wedgie-dev/blob/main/public/code.md
- https://github.com/clawdbotatg/wedgie-dev/blob/main/docs/APPS.md
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/lcd.py
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/save.py
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/wedgie.py
- https://github.com/clawdbotatg/wedgie-dev/blob/main/src/apps/appjson.mjs
- https://github.com/clawdbotatg/wedgie-starter/blob/main/dodge/dodge.py
- https://github.com/clawdbotatg/wedgie-starter/blob/main/hilo/hilo.py
- https://github.com/clawdbotatg/wedgie-starter/blob/main/wedgie.json
