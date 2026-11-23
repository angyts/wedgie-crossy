"""Reproducible offline sweep for mixed terrain feasibility.

Usage:
    python tools/sweep_mixed_terrain.py --seeds 1000 --phases 4
    python tools/sweep_mixed_terrain.py --seeds 1000 --phases 4 --json reports/mixed_sweep.json

A witness is NOT a human-fairness certificate. Non-witnesses may be due to
the deliberately bounded search. Never enable live terrain from these results
without additional timing, join and hardware validation.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import crossy_mixed_validator as validator
import crossy_worldgen as worldgen

# Block 0 starts row 8, block 4 starts row 56, block 10 starts row 128.
BANDS = (0, 4, 10)
KNOWN_SEEDS = (0x3F564588, 0x0676964C)


def sweep(seeds=1000, phases=4, ticks=72, blocks=2, max_failures=30):
    if min(seeds, phases, ticks, blocks) <= 0:
        raise ValueError("seeds, phases, ticks and blocks must be positive")
    if max_failures < 0:
        raise ValueError("max_failures must be nonnegative")
    counts = {}
    failures = []
    total = 0
    passed = 0
    start = time.monotonic()
    # First two seeds preserve known hardware regressions, then a fixed
    # deterministic seed stream. No device RNG and no process-global random.
    for n in range(seeds):
        seed = KNOWN_SEEDS[n] if n < len(KNOWN_SEEDS) else worldgen.mix32(n)
        for block in BANDS:
            key = str(block)
            if key not in counts:
                counts[key] = {"attempts": 0, "witnesses": 0, "no_witness": 0,
                               "all_phases_passed": 0, "seed_groups": 0}
            group_passed = True
            for phase in range(phases):
                witness = validator.joined_route(
                    seed, block, blocks, phase, ticks)
                counts[key]["attempts"] += 1
                total += 1
                if witness is None:
                    group_passed = False
                    counts[key]["no_witness"] += 1
                    if len(failures) < max_failures:
                        failures.append({"seed": "%08X" % seed,
                                         "first_block": block,
                                         "phase": phase,
                                         "reason": "no_witness_within_bound"})
                else:
                    path, ending_phase, ending_col = witness
                    replay = validator.replay_joined_route(
                        seed, block, path, start_phase=phase)
                    goal = 8 + (block + blocks) * worldgen.BLOCK
                    if (replay != (goal, ending_col)
                            or ending_phase != phase + len(path)):
                        raise AssertionError(
                            "invalid witness seed=%08X block=%d phase=%d"
                            % (seed, block, phase))
                    counts[key]["witnesses"] += 1
                    passed += 1
            counts[key]["seed_groups"] += 1
            if group_passed:
                counts[key]["all_phases_passed"] += 1
    return {
        "model": "one_action_then_one_hazard_tick",
        "certifies_human_fairness": False,
        "live_terrain_enabled": False,
        "parameters": {"seeds": seeds, "phases": phases, "max_ticks": ticks,
                       "joined_blocks": blocks, "bands": list(BANDS)},
        "total_cases": total,
        "witness_cases": passed,
        "no_witness_cases": total - passed,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "bands": counts,
        "failure_examples": failures,
        "failures_truncated": (total - passed) > len(failures),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=1000)
    parser.add_argument("--phases", type=int, default=4)
    parser.add_argument("--ticks", type=int, default=72)
    parser.add_argument("--blocks", type=int, default=2)
    parser.add_argument("--max-failures", type=int, default=30)
    parser.add_argument("--json", dest="output", default=None)
    args = parser.parse_args(argv)
    result = sweep(args.seeds, args.phases, args.ticks, args.blocks,
                   args.max_failures)
    report = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        directory = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(directory, exist_ok=True)
        with open(args.output, "w") as handle:
            handle.write(report + "\n")
    print(report)
    return 0 if result["no_witness_cases"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
