# Stage 9 — visible score milestone and three small HUD improvements

Built from Stage 8 `e61d877`. At every tenth new row, the score becomes yellow and is drawn twice (1px offset for boldness) with an `x10` marker for 900ms. It then returns to normal even without further movement; there is no center-screen popup. The HUD adds a ten-row progress bar, highlights BEST when the current score equals the record, and displays a small Y pause hint. The existing Y pause, B resume and A new run in the pause menu remain unchanged. No moving hazards or new generation rules.

Hardware checks: reach score 10 and wait; the bold yellow score should revert after about one second. Check progress bar fills over 1..9, BEST highlight when matching, Y opens pause and B resumes. CI host tests cover HUD drawing; device verification is required.
