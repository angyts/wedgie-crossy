# Phase-aware successor audit (experimental)

The audit enumerates the bounded joint hazard period, records exact
player/tick/camera states at a selected boundary, and checks continuation
from EACH recorded state under the same absolute hazard timeline.
Unreachable boundaries and state-count cap violations fail closed.
The output remains deployable=false.

This is not a complete composition proof: the continuation search uses
a separate finite horizon, checks only a selected boundary, and relies
on provisional instantaneous movement and camera rules. State counts
may grow quickly. The approved generator remains grass-only.
