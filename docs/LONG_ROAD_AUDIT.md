# Long-road audit (offline prototype)

Builds up to four alternating-direction roads with intervening grass
rows, and evaluates whole-join reachability plus all-boundary
continuation under one deadline. Evidence is always deployable=false.

The finite search does not establish universal fairness. A shared
deadline is enforced for continuation, but the current tracer explores
all states within its own horizon. Hazard phase and camera mechanics
remain provisional. ApprovedWorld remains grass-only.
