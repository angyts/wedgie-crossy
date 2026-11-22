# Boundary-state propagation prototype

The new trace_boundaries search carries player position, hazard tick and
camera state through every joined section without restarting the clock
at a boundary. It reports the number of reachable states at each
section's final row. It uses the same step_fp transition as the host
simulation, with a fixed finite horizon.

This is an exploratory diagnostic, not a compositional certificate:
- It currently checks one specified hazard entry phase per invocation.
- Boundary counts do not describe compatible states for arbitrary
  future sections or guarantee that all reachable states can continue.
- Camera behavior and instantaneous player movement remain provisional.
- The approved runtime generator still emits grass only.

Next: formalize entry/exit state sets, check all bounded phases and
adversarial joins, and only then allow hazard sections into ApprovedWorld.
