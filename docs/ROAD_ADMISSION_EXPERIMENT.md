# Road admission experiment — offline only

This experiment builds a five-row grass/road/grass/road/grass fixture
and gathers two independent diagnostics: a whole-join phase sweep and
a phase-aware exact-state successor audit. It records both results
without changing ApprovedWorld or claiming deployment approval.

The review is intentionally not a certificate: the successor audit
covers only one boundary, and both searches use finite horizons and
provisional tick/camera physics. The checker has not been demonstrated
equivalent to actual device gameplay, nor has arbitrary generator
composition been established. Both deployable and runtime_allowlisted
are always false.

Next: investigate counterexamples, enforce all-boundary continuation,
and validate runtime-consistent physics before modifying the allowlist.
