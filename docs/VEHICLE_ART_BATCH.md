# Gameplay art batch — 2026-11-23

## Change
Added a fourth deterministic 20x20 vehicle variant (compact flat-roof truck) alongside hatchback, sedan and delivery van. The style repeats by road band, uses the existing palette and collision tile, and requires no extra sprites, files, heap buffers or LCD transfers. Added a host test for all four variants' rectangle bounds.

## Preserved
- Hardware-accepted smooth car motion, partial LCD refresh and responsive player movement.
- Cold-boot module split, namespaced root files and existing manifest.
- World generation, log support, scoring, collision, saves and difficulty.
- Known test seeds: 0x3F564588 (car jitter), 0x0676964C (dense logs).

## Mixed terrain and smooth logs
Not enabled in this batch. The current generator produces homogeneous hazard sections; mixed road/log/lily joins need time-aware route validation. Smooth log motion previously caused missed joystick presses on dense log sections; reintroduce only with a frame budget and input tests.

## Verification and rollback
Host tests and physical hardware have NOT been run on this new art batch. Run `python -m unittest discover -s tests -v` before installing. On-device, test cold boot, road motion, both known seeds and log input responsiveness. Revert commits `a53d3f4` and `2ef0647` if necessary. Earlier accepted gameplay checkpoint: `869406f`.
