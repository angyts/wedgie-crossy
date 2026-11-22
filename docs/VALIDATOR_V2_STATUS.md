# Swept road validator experiment

`crossy_core.validator_v2.validate_swept_roads` integrates the fixed-point
swept hazard primitive into a discrete time-expanded path search for grass
and roads. Unlike the original occupancy-only validator, it considers every
position traversed by traffic during a tick. It also supports an explicit
initial reaction delay and requires reachability for every supplied entry
phase.

**Limitations:** Moves are instantaneous at tick boundaries; player motion
is not swept. The model has no camera pressure or train warning behavior.
River and rail rows explicitly raise NotImplementedError rather than
silently pretending to validate them. A finite list of phases is not
universal certification, and safe entry/exit states across generated
sections are not yet checked.

This is an incremental prototype. Neither validator is wired into
runtime world generation, and no generated family is certified. Next:
add sub-tile player motion, log carry, rail warning semantics, camera
pressure and section-boundary state compatibility before runtime selection.
