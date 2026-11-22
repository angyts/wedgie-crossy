# Adversarial phase sweep (experimental)

The offline sweep checks a complete joined sequence at every discrete
hazard phase in its bounded repeat cycle. It reports failing phases,
minimum reachable boundary-state counts and explicit deployable=false.
Oversized phase domains and invalid train schedules fail closed.

This is NOT a certification or approval of hazard sections for runtime.
The existing boundary-state prototype uses finite horizons and
instantaneous moves, and searches for SOME successful route per phase.
It does not establish compatibility from every reachable exit state,
human reaction fairness or real-device behavior. ApprovedWorld remains
grass-only.

Next: refine and test phase-specific exit-state contracts, use adversarial
counterexamples to improve pattern families, and only then enable
reviewed hazards in the approved generator.
