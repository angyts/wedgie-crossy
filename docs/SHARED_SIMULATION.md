# Milestone 2.5 — Shared simulation experiment

The new `crossy_core.simulation.step` is a single transition function
used by `crossy_core.shared_validator.validate_shared`. Both use the
same instantaneous-at-tick-start player movement and swept road hazard
occupancy over that tick. This eliminates one class of divergence between
the *host-side grass/road* validator and gameplay simulation.

**Not a completed unified gameplay model.** The actual Wedgie runtime
does not exist yet. River support/drift, train geometry/warnings,
continuous player movement, camera pressure, section-state compatibility,
and complete phase certification remain open. The older validators are
preserved as prototypes; none certify generator output.

Run `python -m unittest discover -s tests -v` and review the CI result.
