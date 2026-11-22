# First on-device MicroPython prototype

`crossy.py` and root `wedgie.json` form an installable Wedgie cartridge using the documented `LCD`, `Keys`, `save` and optional `wedgie.rand_below` interfaces. It has grass, trees, movement, scoring, restart and a simple rising camera-pressure timer. No Rust binary is needed to launch it.

This is an independent early gameplay prototype, **not** a port of the certified Python generator or Rust game engine. It uses a simplified procedural tree generator with a guaranteed clear central column. The host CI cannot execute hardware display calls; test first in the Wedgie emulator, then on the physical device. Measure RAM, frame time and actual button behavior. Roads, rivers and trains remain disabled.
