# Hazard candidate catalog: offline exploration only

This milestone adds small reproducible grass-hazard-grass sections for
roads, rivers and railways. Each candidate can be screened across the
complete bounded discrete hazard phase cycle with camera-aware search.
The result includes explicit evidence and a deployable=false flag.

A positive screening result is **not** a compositional certificate:
the route may end in an incompatible column, phase or camera state for
the next section. Instantaneous player moves and simplified hazard
physics remain provisional. No candidate is automatically accepted by
the runtime allowlist; ApprovedWorld still emits grass only.

Before allowing hazards in the actual generator, establish explicit
entry/exit state transfer and validate chained sections with persistent
camera and hazard timing. Keep the failure policy conservative.
