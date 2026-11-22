# Stage 6 — bounded endless grass prototype

Last physically verified checkpoint: `63eb042` (score, HUD, restart). This commit introduces a 12-row ring buffer, vertical camera following, and deterministic row-by-row tree generation. The central column (5) is always open. A fixed seed makes hardware runs reproducible; A resets the run. Moving backward into evicted rows is blocked. No roads, rivers, trains, save writes or hardware RNG yet.

Verify on Wedgie: move up at least 20 rows; watch SCORE and scrolling; use left/right around trees; ensure no alignment drift; press A and verify initial layout and SCORE 0. Host tests exercise deterministic generation and one million row advances. This is not a human fairness certificate. Debug messages include position, score and world window. Keep Stage 5 as the rollback point until this build is verified.
