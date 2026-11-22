# Hardware stage 4 — fixed trees and collision blocking

Last hardware-verified checkpoint: `e00a49b` (grass grid and movement). This stage adds exactly six static trees at fixed grid coordinates and prevents the chicken from entering their cells. The start tile is clear. The tree immediately right of the starting chicken is intentionally blocked; moving up remains possible. No scrolling, random generation, scoring or moving hazards.

Expected physical test: the chicken begins at grid column 5, row 9. Press right: no movement. Press up: moves one tile. Press left from there: blocked by a tree at column 4, row 8. Press down and then left: movement succeeds. Debug prints distinguish blocked and successful inputs. Host smoke tests verify the fixed layout, collisions and rendering count. Reinstall with `git pull origin hardware-baseline && python wedgie.py install .` and verify before advancing.
