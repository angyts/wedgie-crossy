# Physics primitives (Milestone 2.1, partial)

Host-side fixed-point geometry uses 256 units per tile. Swept periodic
obstacle overlap detects collisions between tick endpoints, including
wraparound and both movement directions. River support checks that the
entire player footprint begins on one log and carries it by an integer
delta; unsupported or offscreen positions fail.

**Scope:** These are standalone primitives, not yet wired into the
time-expanded validator or a runtime game loop. The swept collision
primitive treats the player as stationary for the tick; relative motion
must be supplied when the player moves. The river primitive assumes
same-log support during the tick and does not yet check collisions with
other obstacles or model transitions between moving logs.

**Not implemented:** player movement interpolation, train approach and
warning semantics, human reaction allowance, camera pressure, phase
enumeration/certification, integration into world generation. No
physical-hardware timing or memory measurements have been performed.

Run: `python -m unittest discover -s tests -v`.
