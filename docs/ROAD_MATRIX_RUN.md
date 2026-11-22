# Run actual offline road counterexample matrix

Run from repository root:

```bash
python scripts/audit_road_matrix.py > road-audit.json
```

The JSON captures eight fixed road configurations with different
speeds, spacing, lengths and road counts, plus the phase/boundary
continuation failures for each. Preserve the output when comparing
future changes. A failure may reflect an impossible crossing, a short
deadline, or conservative provisional validator assumptions; the
result alone does not distinguish these explanations.

This script performs analysis, not gameplay certification. No
configuration becomes runtime-approved. The generator remains grass-only.
