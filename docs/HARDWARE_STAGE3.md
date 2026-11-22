# Hardware stage 3: 12x12 grass grid

Last physically verified checkpoint: `9484470` (joystick movement). This stage draws 12x12 alternating green 20px tiles using only `lcd.fill_rect`, keeps joystick movement aligned to tile centers, and reduces the chicken to fit inside a single tile. The top two rows show the GRID TEST diagnostic title; no hazards, scrolling, scoring or procedural generation are introduced. Debug checkpoints remain enabled.

Host smoke tests check the 72 alternate grass rectangles, six chicken rectangles, display bounds, joystick alignment and single initial display flush. Install with `git switch hardware-baseline && git pull origin hardware-baseline && python wedgie.py install .`. Verify all four directions, tile alignment and no visual corruption. Hardware verification is required before further changes.
