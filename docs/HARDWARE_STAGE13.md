# Stage 13 — traffic speed and crash presentation

Five additions: cars advance every 3 active frames instead of 6; sprites have body, windshield and wheels; impact draws a five-step pixel starburst; game-over reads ALWAYS LOOK / BEFORE YOU / CROSS THE ROAD and YOUR SCORE; green button icon invites NEW RUN. The crash animation lasts approximately 450 ms and does not update the persistent high score in DEV_MODE. Existing score, pause, and traffic movement rules remain. Hardware verification and complete CI are required before treating this release as stable.
