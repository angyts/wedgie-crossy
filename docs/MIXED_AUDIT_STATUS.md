# Mixed-terrain adversarial audit (offline prototype)

The new mixed_audit module constructs complete grass/road/river/rail
sequences with contiguous absolute row indices. It enumerates all
ordered hazard families up to three hazards, then runs the existing
whole-join phase sweep with a single camera and hazard timeline.
Oversized phase domains are recorded as rejected cases rather than
being silently skipped. All results explicitly set deployable=false.

This is diagnostic testing, NOT a compositional fairness proof. The
prototype has instantaneous player moves, simplified log carry and
camera behavior, and existential reachability from specified entries.
The approved runtime generator remains grass-only.

Next: model section contracts as actual sets of (column, subtile
offset, time phase, camera state) and prove continuation from the
relevant reachable exit states, rather than relying on aggregate
boundary counts. Only then consider allowing reviewed hazards.
