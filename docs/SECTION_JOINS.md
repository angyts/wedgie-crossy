# Section joins: prototype integration

The join helper checks contiguous absolute row indices and enforces the
five-consecutive-dangerous-row cap **across** section boundaries.
It passes the entire concatenated row sequence to validator_v3, so
reachability is evaluated across the join rather than by combining
independent yes/no results.

This is not a production fairness certificate. The v3 model still
approximates rail trains as full-row pulses, makes instantaneous
player moves at tick boundaries, and approximates camera pressure
with a consecutive-wait bound. Only supplied entry phases are checked.
An empty or disconnected set of entry states cannot be certified.
The generator does not yet consume validated pattern families.

Next: replace the simplified physics with a single runtime-consistent
movement/collision model, enumerate a justified phase domain, model
camera pursuit and verify end-state compatibility for chained sections.
