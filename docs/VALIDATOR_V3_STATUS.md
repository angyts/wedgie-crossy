# Multi-terrain validator prototype v3

This experiment adds river log carry, periodic whole-row train occupancy,
train warning entry restrictions, and a consecutive-wait limit as a rough
camera-pressure proxy to the host-only time-expanded search.

**Not certified:** Train direction/speed are not yet represented as moving
train geometry. Player moves are instantaneous at tick boundaries; swept
relative player/hazard motion is absent. Log support is tested at tick
start and the player is carried through the tick, but no interpolation
or log-switch transition is modeled. A consecutive-wait bound is not the
rising camera boundary described in the specification. Testing selected
entry phases is not proof across all phases or all section joins.

Do not wire this validator into runtime generation as a fairness guarantee.
Next work: unify the player/hazard continuous-time contract, define
phase-complete section entry/exit compatibility and implement actual
camera pressure. Tests: python -m unittest discover -s tests -v
