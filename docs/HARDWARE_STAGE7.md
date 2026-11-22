# Stage 7: pause, best score and milestones

Based on Stage 6b (`f805855`), pending physical confirmation of the palette adjustment. Y toggles pause and blocks movement until Y is pressed again. The best score is loaded with `save.load('best', 0)`, shown in the HUD and persisted with `save.store` only at 10-row milestones or A-button reset if it is a new best. Milestone text appears at score 10, 20, etc., until the next movement redraw. A restarts the deterministic world; it does not erase best score. No roads or other hazards.

On device: test Y pause, movement suppression, Y resume, score 10 milestone, A reset and retained BEST. The last fully verified gameplay checkpoint is `9c5d449`; verify the Stage 6b palette before treating this build as the new baseline.
