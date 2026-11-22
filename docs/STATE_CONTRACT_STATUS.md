# Exact boundary-state diagnostics

The experimental trace_contracts search records explicit state tuples:
(local row, fixed-point horizontal position, absolute hazard tick,
camera best row, camera last-progress tick, camera death boundary).
These are retained across complete joined sections; the search does
not collapse boundary states to counts.

This does NOT establish universal or compositional safety. It currently
finds some route from supplied entry columns and one phase, with finite
horizon and the provisional instantaneous-move/camera model. Exact
states are available for future successor-state compatibility checks,
but the tool does not yet demand safe continuation from every relevant
reachable exit state. Search memory can grow rapidly with horizon.

ApprovedWorld remains grass-only. Do not admit hazard candidates
based solely on these diagnostics. Next: bounded state-set transfer
contracts, dominance pruning, adversarial successor tests and actual
runtime-consistent timing.
