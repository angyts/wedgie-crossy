# Single end-to-end deadline (offline prototype)

The phase successor audit now accepts optional total_horizon. Every
recorded boundary state receives only the ticks remaining before the
original journey deadline, rather than a fresh full budget. The
all-boundary wrapper forwards the same deadline to each boundary.
Without total_horizon the legacy separate continuation horizon remains.

This is a conservative diagnostic, not a deployment certificate. A
state arriving at the deadline may count as successful only if already
on the final row. The trace still explores its own horizon and records
all arrivals; only the continuation step enforces the shared deadline.
Instantaneous moves, finite state exploration and provisional camera
rules remain limitations. ApprovedWorld remains grass-only.
