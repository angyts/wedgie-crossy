"""Classify the eight reproducible road configurations by boundary state.

Run: python3 scripts/classify_road_matrix.py > road-classifications.json
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.audit_road_matrix import CONFIGURATIONS
from crossy_core.long_road_audit import road_sections
from crossy_core.road_outcomes import classify_boundary

def run(horizon=8, max_period=64, max_states=4096):
    if type(horizon) is not int or horizon < 1:
        raise ValueError("invalid horizon")
    reports = []
    for count, speed, spacing, length in CONFIGURATIONS:
        sections = road_sections(count, speed, spacing, length)
        boundary_reports = tuple(
            classify_boundary(sections, boundary_index=index,
                              horizon=horizon, max_period=max_period,
                              max_states=max_states)
            for index in range(len(sections)-1)
        )
        reports.append({
            "configuration": (count, speed, spacing, length, horizon),
            "boundaries": boundary_reports,
            "deployable": False,
        })
    return {"cases": len(reports), "horizon": horizon,
            "reports": tuple(reports), "deployable": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=8)
    parser.add_argument("--max-period", type=int, default=64)
    parser.add_argument("--max-states", type=int, default=4096)
    args = parser.parse_args()
    print(json.dumps(run(args.horizon, args.max_period, args.max_states),
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
