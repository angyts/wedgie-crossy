# Hardware checkpoint 2 — joystick movement

Based on hardware-verified stage 1 commit `f5f50a0`. Changes only the position of the existing six-rectangle chicken in response to edge-triggered `Keys().pressed()` events. Moves are 20 pixels per press. X stays within 10..210 and Y within 169..209 so the sprite remains on the display and clear of the diagnostic text. No held-key repeat, scrolling, collision, score or world generation.

`DEBUG = True` logs directional moves and startup checkpoints. The scene redraws only when position changes. Host smoke tests check startup, static drawing, movement and bounds; hardware still needs verification.

Install after `git switch hardware-baseline && git pull origin hardware-baseline`: `python wedgie.py install .`. Test all four joystick directions and edges, and confirm no spontaneous movement. If it fails, restore `f5f50a0`.
