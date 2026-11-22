# Stage 11: five-feature static-road prototype

Five connected additions: (1) sparse road terrain every 12 rows from row 6, (2) simple dashed road markings, (3) deterministic stationary red cars, (4) lethal car contact with a CRASH overlay, and (5) green-button A restart from game over. Cars are NOT moving yet. The central column remains clear; tree rows remain unchanged. This is not a validated moving-traffic engine. Pause, scoring and bounded world remain. Test the full Python suite and hardware before advancing.

The old sprite test now checks minimum rectangle count plus bounding box, rather than assuming six rectangles for every orientation. This change should be verified by CI; no claim of a passing suite is made until observed.
