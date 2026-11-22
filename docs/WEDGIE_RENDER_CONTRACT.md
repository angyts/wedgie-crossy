# Device-independent Wedgie rendering contract

The Rust no_std runtime exposes `render::snapshot`, producing a fixed 12x16 tile snapshot with `Empty`, `Grass`, `Tree`, and `Chicken` tile values, an absolute first-row index, score, and game-over flag. Screen row 0 represents the oldest visible row. No graphics or framebuffer driver is linked. The device adapter will map these tiles onto the actual Wedgie display API.

This is a grass-only rendering milestone; hazards, sprites, buttons, screen refresh and actual firmware integration are not implemented. The approved generator remains grass-only.
