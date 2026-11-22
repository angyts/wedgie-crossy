# Camera-pressure prototype

Camera tracks furthest-forward row, the tick of last new progress, and a
monotonically rising death boundary. Only reaching a NEW furthest row
resets the inactivity clock. Grace and pressure cadence are configurable
integer ticks. The time-expanded validator keeps camera state separately
for each candidate path and invokes the same fixed-point simulation.

**Important design choice:** The boundary is monotonic and does not
retreat after progress. This is a proposed rule, not yet a measured or
playtested implementation of the specification's camera behavior.

**Not certified:** The actual game runtime does not yet exist; train
schedules and terrain generation are not constrained to certified
families. Continuous player motion, full phase coverage, section exit
compatibility and human reaction allowances require more work.
The five-second grace period remains provisional until a tick rate is
selected and tested on Wedgie hardware.
