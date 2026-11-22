# All-boundary continuation audit — offline only

This wrapper checks every internal section boundary, rather than
selecting only the first. Each check enumerates bounded joint hazard
phases and evaluates continuation from exact recorded boundary states.
Any failed boundary causes the aggregate audit to fail.

This is NOT a deployment certificate. The underlying continuation
search uses a fresh finite horizon for each boundary and therefore
does not yet enforce one total journey-time budget. The model is
provisional and the approved runtime generator remains grass-only.

Next: enforce a single end-to-end time budget, test longer road
sequences, and resolve counterexamples before admitting hazards.
