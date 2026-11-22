# Wedgie grass game loop

The no_std Game type owns player, camera, tick, score, death flag and a fixed 16-row world window. Each call to step processes one input. Tree collisions block and consume a tick. Out-of-window movement, invalid coordinates and tick overflow fail closed. Death is terminal.

This is not a device application: no button mapping, screen driver, game clock or native firmware integration exists. The initial grass-only loop is intended for host-side verification and later porting to the actual Wedgie firmware environment.
