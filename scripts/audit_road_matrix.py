"""Run a bounded, reproducible offline road audit and print JSON evidence.

Usage: python scripts/audit_road_matrix.py
       python scripts/audit_road_matrix.py --horizon 8 --max-period 64
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crossy_core.road_counterexamples import inspect_matrix

CONFIGURATIONS = (
    (1, 1, 8, 2),
    (1, 2, 8, 2),
    (1, 3, 8, 2),
    (2, 1, 8, 2),
    (2, 2, 8, 2),
    (2, 3, 8, 2),
    (2, 2, 10, 2),
    (2, 2, 10, 3),
)

def run(horizon=8, max_period=64):
    reports = inspect_matrix(CONFIGURATIONS, horizon=horizon,
                             max_period=max_period)
    return {
        "model": "offline-road-counterexample-prototype",
        "horizon": horizon,
        "max_period": max_period,
        "cases": len(reports),
        "passed": sum(bool(r["passed"]) for r in reports),
        "failed": sum(not r["passed"] for r in reports),
        "reports": reports,
        "deployable": False,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=8)
    parser.add_argument("--max-period", type=int, default=64)
    args = parser.parse_args()
    print(json.dumps(run(args.horizon, args.max_period),
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
