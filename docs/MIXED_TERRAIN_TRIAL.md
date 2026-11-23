# Mixed terrain — controlled hardware trial

## Enabled
`crossy_worldgen.MIXED_TERRAIN = True` on main for a physical Wedgie trial. Selected interior road lanes in existing sections become moving-log lanes. Grass buffers and first/last road lanes remain unchanged. The main game uses the shared section() function for terrain, masks, drawing and collision.

## Evidence and limitations
- User previously reported 302 host tests passing with the feature flag OFF.
- User's offline sweep found 1,200/1,200 witness routes across 100 seeds, four phases and three bands under a simplified one-action-per-traffic-tick model.
- **The current flag-ON build has not been tested on hardware or through the full host suite.**
- Offline route witnesses are not a proof of human reaction-time fairness, swept collisions, input latency or universal seed reachability.
- Dense moving logs previously caused low FPS and missed joystick inputs.

## Trial procedure
1. `git pull origin main`
2. `python -m unittest discover -s tests -v`
3. `python wedgie.py install .`
4. Unplug/replug and launch without running debug; confirm cold boot.
5. Cross mixed road/log sections and check that visual support, collision and carry agree.
6. Watch for 2-FPS log sections, missed presses, frozen cars, HUD corruption and unusual heap swings.
7. Revisit known seeds 0x3F564588 and 0x0676964C using FIXED_SEED for reproduction.

## Immediate rollback
Change `MIXED_TERRAIN = True` back to `False` in `crossy_worldgen.py`, reinstall, and rerun tests. Or revert trial commits `3a7245e` and `86d00d9`. Do not modify firmware.
