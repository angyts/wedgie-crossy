# Stage 4 alignment correction

Physical observation: the chicken sprite visually straddled tiles while trees appeared offset. The tree coordinates already use tile origins `(col*20, row*20)` and collision uses the chicken's logical position `(10+col*20, 9+row*20)`. The chicken renderer now subtracts those logical offsets before drawing. This keeps every chicken rectangle inside its occupied tile and preserves the tree collision logic unchanged.

One regression test checks chicken rectangles at the upper-left, starting and lower-right tiles. Reinstall and verify visually. Previous hardware-verified tree/collision commit: `0d48a27`.
