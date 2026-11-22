# Stage 8 — unobtrusive milestones and pause menu

Built on Stage 7 (`b4ec8a8`). Changes: no center-screen row milestone popup; a subtle 2-pixel highlight in the top-left score area at multiples of ten. The HUD shows only SCORE and BEST. Y opens pause; red B resumes (Y also resumes for compatibility). Green A starts a fresh run only from pause. The chicken faces left or right after a successful horizontal movement. The saved best score is written at ten-row milestones or when starting a new run from pause; flash is not written on every move.

Test on hardware: move to score 10 without an overlay; check the score highlight; Y pause; B resume; Y pause then A new run; check BEST persists after a saved milestone. All changes require hardware confirmation. The prior gameplay checkpoint remains available for rollback.
