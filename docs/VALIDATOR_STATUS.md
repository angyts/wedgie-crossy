# Offline validator prototype status

This is **not** the locked fairness validator or an approval to deploy
generated sections. It is an initial, host-only discrete time-expanded
reachability prototype.

## Current assumptions
- One tick is one movement opportunity; move exactly one cardinal tile or wait.
- Entry state is a supplied set of columns on the first row.
- Hazards are sampled at integer ticks, with whole-column occupancy.
- Roads have periodic blocked cells; rivers have periodic supported cells.
- Trains block the full row for a periodic interval.
- A route must survive both source and destination occupancy at each tick.
- The search checks a finite horizon and explicitly supplied entry phases.
- The prototype checks an entire supplied section, including row joins.

## Not yet modeled (release blockers)
- Continuous/swept collision between ticks; fast traffic can tunnel.
- River log support and horizontal carry/drift between ticks.
- Real train approach, warning timing, direction and speed.
- Human reaction allowance, crossing windows, and camera pressure.
- Boundary compatibility across arbitrary generated section joins.
- Exhaustive parameter ranges, all relevant entry phases, and runtime
  selection exclusively from certified pattern families.

## Next steps
Develop fixed-point substep hazard trajectories and river carry, specify
time and reaction units, add adversarial fixtures, then certify only bounded
parameter families with explicit assumptions. The current world generator
remains **provisional and uncertified**.
