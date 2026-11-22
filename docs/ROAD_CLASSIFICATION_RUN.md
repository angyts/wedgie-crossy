# Classify road audit outcomes

From the repository root:

```bash
python3 scripts/classify_road_matrix.py > road-classifications.json
```

The output enumerates the same eight configurations as the road audit,
but reports each boundary and phase as unreachable, nonviable, mixed,
all-recorded-states-continue, or state-cap-exceeded. This distinguishes
the existence of some successful route from the much stricter claim
that every reachable boundary state can continue before the deadline.

Do not interpret a positive result as human fairness or permission to
enable traffic in ApprovedWorld. The generator remains grass-only.
