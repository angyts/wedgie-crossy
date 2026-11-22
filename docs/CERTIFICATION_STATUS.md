# Finite-domain section screening (experimental)

`crossy_core.certification.screen_section` enumerates every discrete
hazard phase in the least-common-multiple repeat cycle, up to a strict
configurable cap. If the phase domain exceeds the cap, it fails closed
instead of sampling a few favorable phases. The screen also checks
contiguous indices, a five-danger-row limit, and train schedules.
It delegates route search to the existing camera-aware fixed-point
prototype and returns an evidence record with the exact assumptions.

**This is NOT certified world generation.** Each phase is evaluated from
the same specified initial grass-column set, and an existential route
is sufficient for that phase. A path from one section's exit state
is not yet passed into the next section's entry state. The simplified
instantaneous movement contract and camera behavior are provisional.
A finite search horizon cannot prove arbitrary playability. The
generator still selects uncertified candidate rows.

Next: add explicit exit-state sets and compatible joins, constrain the
generator to reviewed parameter families, and adversarially test
the resulting composition. Do not label sections production-certified.
