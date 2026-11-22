# Procedural world prototype

This branch intentionally does **not** replace the hardware-verified Crossy
game yet. It adds a pure, reproducible world generator and host-side tests.

- Different 32-bit seeds produce different terrain layouts.
- Each 16-row block contains 1–8 road, log-river or lily-river rows,
  followed by at least eight grass rows.
- Adjacent road/log lanes alternate direction.
- Lily-pad rivers have a guaranteed static central pad in every row.
- Grass-bank tree generation never blocks the central column.
- Generator stores no rows or heap-growing history.

**Important limitation:** The static lily route does not prove that every
moving-log or road crossing is safe at every traffic phase. Before integration,
the generator needs a time-expanded reachability validator, device profiling,
and a compatibility layer to keep render/collision behavior identical.
No hardware flash or high-score write is required for these host tests.

Run: `python -m unittest tests/test_worldgen.py -v` (or discovery).
