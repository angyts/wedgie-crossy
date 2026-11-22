# Wedgie Crossy — Hardware and Starter Repository Audit

Audit date: 2026-11-22
Scope: read-only review of `clawdbotatg/wedgie-starter` and `clawdbotatg/wedgie-dev` on their `main` branches.
Purpose: translate the actual app/firmware interfaces into implementation constraints for `angyts/wedgie-crossy`.

This is a source audit, not a claim of on-device testing. No upstream repositories were modified.

## 1. Repositories and roles

- [wedgie-starter](https://github.com/clawdbotatg/wedgie-starter) is the app template and contains two complete MicroPython games: Dodge and Hi-Lo. Dodge is the best reference for a continuously animated game loop and prebuilt sprites; Hi-Lo is the useful reference for hardware-backed randomness, saves, and event-driven input.
- [wedgie-dev](https://github.com/clawdbotatg/wedgie-dev) contains the site, firmware, emulator, and the authoritative app-building guide. The relevant source files reviewed include `public/code.md`, `docs/APPS.md`, `firmware/lcd.py`, `firmware/save.py`, and `firmware/wedgie.py`.
- Wedgie apps are separate repositories. Crossy should remain in `angyts/wedgie-crossy`; do not add game code to the firmware repository.

## 2. Hardware/display facts verified in source

- The supported screen described by the firmware is 240x240. Input is a 5-way joystick (up/down/left/right/press) plus A/B/X/Y.
- The current `firmware/lcd.py` creates a singleton-style shared 4-bit `framebuf.GS4_HMSB` display buffer: 240 x 240 x 4 bits = 28,800 bytes (about 28.1 KiB). It replaced the older full RGB565 framebuffer to leave more heap available.
- The palette has 16 entries. `lcd.color(r,g,b)` returns the nearest palette index; `lcd.tint()` can temporarily remap a palette slot on supported firmware. A sprite can be a `framebuf.FrameBuffer` and drawn with MicroPython's `blit` using a transparent key and optional palette.
- C-backed drawing operations inherited from MicroPython's FrameBuffer (for example fill, fill_rect, rect, hline, vline, line, text, blit, scroll) are preferable to Python loops over individual pixels.
- The firmware guide reports approximately 130–150 KB RAM free for an app on an RP2040 after the display framebuffer is reserved. Treat this as a documented observed range, not a guaranteed budget: measure the target board and peak game state.
- The source guide's older benchmark table reports a full-screen push around 25 ms and recommends partial pushes. Its measurements are explicitly from an earlier display implementation; remeasure on the firmware actually installed on the target Wedgie before locking the frame budget.

### Important display pipeline correction

The starter Dodge comments describe a frame being sent by DMA while the next update runs, using `show_start()` / `show_wait()`. In the currently audited `firmware/lcd.py`, these are retained for compatibility only:
- `show_start()` calls `show()` synchronously.
- `show_wait()` is a no-op.

Therefore do not depend on asynchronous DMA overlap. Use the current `lcd.show(y0, y1)` and/or `lcd.show_rect(x, y, w, h)` dirty-region methods, and profile their real cost on the board. Avoid a full-screen push every frame unless measurement proves it fits.

## 3. Input contract

The firmware provides `from lcd import LCD, Keys, color`.

- `Keys().pressed()` returns key names that went down since the previous read: `A`, `B`, `X`, `Y`, `up`, `down`, `left`, `right`, `press`.
- `Keys().held(name)` reports a held direction/button (including the firmware's virtual key presses).
- `Keys(physical=True)` deliberately ignores virtual USB-injected presses. Ordinary games should use the default `Keys()` so emulator/USB testing can drive gameplay.
- The app should poll keys as part of its loop and include a small sleep each iteration. The firmware services USB during these sleeps. Do not busy-spin.

For Crossy, use edge-triggered `pressed()` for one-tile movement. Add a controlled repeat policy only if playtesting shows it is needed; avoid moving multiple tiles from one held input by accident.

## 4. Randomness: hardware source and deterministic tests

The firmware exposes `from wedgie import rand_below, rand_source`.

- `rand_below(n)` returns a uniformly distributed integer in `[0, n)`; the current implementation uses rejection sampling to avoid modulo bias.
- `rand_source()` reports the source selected by firmware, such as `ATECC608`, `OPTIGA Trust M`, or an `os.urandom` fallback with a reason.
- The firmware's `rand()` implementation selects the secure-chip source when available/working, otherwise falls back. The game must not claim a secure-chip source without checking `rand_source()`.
- Hi-Lo in wedgie-starter uses Fisher–Yates with `rand_below(i + 1)`, and displays/reports the source. This is a good API usage example.

**Crossy design consequence:** obtain a fresh seed from the platform's hardware-backed random API at the start of a run, then use a small deterministic PRNG seeded with that value for all procedural generation decisions. Keep the seed in debug/test output so a generated run can be replayed. Do not call hardware RNG for every lane/obstacle decision; reproducibility and testability require the deterministic stream after seeding.

The current firmware source is at version `0.3.91` (`VERSION` in `firmware/wedgie.py`) at audit time. The starter's `wedgie.json` declares firmware floor `0.3.5`; Crossy's own floor should be chosen from the APIs it actually uses, not copied blindly. Confirm the user's installed firmware with `python3 wedgie.py debug` before a hardware release.

## 5. Save/persistence contract

The firmware provides `import save` with `save.load(name, default=None)`, `save.store(name, data)`, and `save.delete(name)`.

- Saves are isolated by the running app: firmware stores them under `/saves/<game>/`.
- JSON-compatible values are serialized; bytes-like values are stored as binary.
- Store writes a temporary file and renames it into place; flash-full errors are surfaced as `OSError`.
- Dodge/Hi-Lo update the best score/streak only when improved and save at game-over, not every frame.

For Crossy, load the best score once at startup; persist only a newly improved best score (and any explicitly approved settings), with graceful handling of `OSError`. Do not write per frame or per movement.

## 6. Starter-game patterns worth reusing conceptually

### Dodge
File: [dodge/dodge.py](https://github.com/clawdbotatg/wedgie-starter/blob/main/dodge/dodge.py)

Useful:
- A module-level `LCD()` and `Keys()`, with game state and sprite buffers allocated before entering the hot loop.
- Pixel-art source represented as compact row strings and converted once into 4-bit framebuffers.
- Fixed target loop interval (`FRAME = 25` ms in the example).
- Reused mutable obstacle records rather than creating a new collection every frame.
- Precomputed score strings only when the score changes.
- Saves the best score only on game over.
- Uses the built-in `ui.page` game-over presentation.

Do not copy the old DMA assumption in its comments. Confirm each graphics optimization against the currently installed firmware.

### Hi-Lo
File: [hilo/hilo.py](https://github.com/clawdbotatg/wedgie-starter/blob/main/hilo/hilo.py)

Useful:
- Uses `wedgie.rand_below` and `rand_source` rather than Python's unseeded `random` for security-chip randomness.
- Fisher–Yates shuffle is appropriate when a uniformly shuffled finite set is needed.
- Saves record performance only when a new best is reached.
- Redraws only after meaningful state changes when nothing animates.

Crossy is animated, so it needs a regular update loop; Hi-Lo's event-driven redraw-only approach does not transfer wholesale.

## 7. App packaging and conventions

The current app format is a folder containing a root `wedgie.json` and the app's Python/assets files. The starter demonstrates an `apps` list with `mod`, `name`, `about`, `files`, `entry: "run"`, and a 12x12 cartridge `icon`.

Important constraints from `public/code.md`:
- `mod` is a Python module name, 2–20 lowercase letters/digits/underscores, beginning with a letter; avoid firmware and MicroPython module names.
- Each declared app file is installed at the flash root under its basename. File basenames must be the module name or begin with `<mod>_`; allowed suffixes include `.py`, `.mpy`, `.bin`, `.json`, `.txt`.
- The main module is required. Up to 30 files and 256 KB per app.
- `entry: "run"` means the firmware imports the module and calls its `run()` function. Keep the import fast and allocate large fixed buffers before entering the loop.
- The `fw` field is a minimum firmware version. The whole current UI kit requires 0.3.36 per the guide; `ui.page`/basic UI is already used by the starter at its 0.3.5 floor. Validate exact API dependencies.
- Use the built-in `ui` components for title/game-over/message UI rather than inventing a separate system look.
- The emulator at `wedgie.dev/code` is useful for iteration but has no useful real-device RAM limit. The virtual Wedgie is closer to device memory and install behavior, but still is not a substitute for a real board's speed and peripherals.
- A public app installed directly from GitHub is unsigned and has full access on the device. This is a trust boundary to state clearly if Crossy is distributed that way. Shelf publication requires the firmware maintainer to review and sign a specific commit.

## 8. Concrete Crossy implementation guidance

1. Keep the generator and pattern validator host-testable Python modules with no `lcd`, `machine`, or hardware imports. This keeps exhaustive/time-aware fairness tests fast and deterministic on desktop.
2. Keep the device app adapter thin: poll `Keys`, advance integer/fixed-point simulation, request only active-row pattern data, draw visible rows/sprites, and sleep to a measured frame target.
3. Avoid per-frame allocations. Preallocate the active row/hazard ring buffers and reuse row descriptors. Do not persist the endless world; persist only seed/score/settings when useful.
4. Use 4-bit sprites or other compact assets. Make a deliberate palette plan for terrain, vehicles, logs, trains, player, UI contrast, and warning states.
5. Implement collisions in simulation coordinates, independent of pixel rendering. Use swept/substep collision for fast-moving hazards; frame rate and sprite drawing must not determine collision fairness.
6. Keep world-generation seed and difficulty band in reproducible test fixtures. The on-device seed can come from `rand_below`/other firmware random bytes; deterministic PRNG state drives every subsequent generation choice.
7. Profile actual frame time, free heap, peak allocations, flash usage, and sustained play on the user's exact board/firmware. The guide's 130–150 KB is an estimate, not an allocation target.

## 9. Next action order

- [ ] Confirm the actual board model and installed firmware using `python3 wedgie.py debug`.
- [ ] Create the host-side pattern schema, deterministic PRNG wrapper, and time-aware section/join validator.
- [ ] Add fixtures for valid and invalid road/river/railway transitions, including moving-object phases and camera-pressure assumptions.
- [ ] Run deterministic million-row stress tests for bounded memory and arithmetic; separately test that fixed seed = fixed output.
- [ ] Only then add the Wedgie `LCD`/`Keys` adapter, partial-dirty rendering, and best-score save.
- [ ] Test in `wedgie.dev/code`, then virtual Wedgie, then the physical board; measure on physical hardware.

## 10. Source links reviewed

- https://github.com/clawdbotatg/wedgie-starter
- https://github.com/clawdbotatg/wedgie-starter/blob/main/dodge/dodge.py
- https://github.com/clawdbotatg/wedgie-starter/blob/main/hilo/hilo.py
- https://github.com/clawdbotatg/wedgie-starter/blob/main/wedgie.json
- https://github.com/clawdbotatg/wedgie-dev
- https://github.com/clawdbotatg/wedgie-dev/blob/main/public/code.md
- https://github.com/clawdbotatg/wedgie-dev/blob/main/docs/APPS.md
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/lcd.py
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/save.py
- https://github.com/clawdbotatg/wedgie-dev/blob/main/firmware/wedgie.py
