# Stage 5: score, HUD, restart

Based on hardware-verified alignment commit `70dd6b5`. Three tightly related features: scoring for the highest row reached (starting row 9), HUD showing SCORE, and A-button reset. Score never decreases when moving down. Trees and collision remain fixed; no random generation, scrolling, camera pressure, or persistence.

Test on Wedgie: start SCORE 0; press up to SCORE 1; move down and verify it remains 1; press A to return to start and SCORE 0. Check that the same tree blocks movement as before. Host tests cover scoring and startup rendering; physical verification is required before moving on.
