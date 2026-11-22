# Road continuation outcome classification (offline)

The classifier enumerates bounded hazard phases and separates:
unreachable boundary, no viable continuation, mixed continuation,
all recorded states continue, and state-cap exceeded.

A mixed result means at least one recorded state has a route to the
end within the shared deadline, but at least one does not. It is not
evidence that a real human can consistently find the viable route.
A positive result is not a gameplay fairness certificate. The
approved generator remains grass-only.
