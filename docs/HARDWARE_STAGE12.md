# Stage 12 — five moving-traffic behaviors and development scoring

Five road behaviors: (1) cars move one tile every six 100ms active frames, (2) adjacent road bands alternate direction, (3) traffic wraps horizontally, (4) stepping onto a car kills the chicken, and (5) a car arriving at an occupied cell also kills the chicken. Pausing stops the traffic clock. The current swept check tests old and new occupancy, not continuous sub-tile physics; full physics parity remains future work.

`DEV_MODE = True` defaults to an in-memory BEST of zero on every launch and performs NO save.load/save.store calls. It does not erase any previously saved best score. To enable release persistence set DEV_MODE False: read saved best at startup, write only when a run ends by crash or a new run is selected from pause, and only if it beats the saved best. No milestone writes. For a genuine flash reset, use Wedgie's supported saves management rather than writing zero repeatedly.

Hardware test: observe moving cars and alternating directions, pause and verify cars freeze, resume, enter a car or wait for a car on a road, check crash and green restart. Tests must pass before deployment.
