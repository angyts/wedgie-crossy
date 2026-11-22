"""Offline audit of every internal section boundary.

Each boundary is checked across the bounded joint hazard phase cycle
using exact player, tick, and camera states. This is diagnostic only:
continuation uses a separate horizon and the provisional tick model.
"""
from .phase_successors import audit_successors

def audit_all_boundaries(sections, **settings):
    if not isinstance(sections, (list, tuple)) or len(sections) < 2:
        raise ValueError("at least two sections required")
    results = tuple(
        audit_successors(sections, boundary_index=i, **settings)
        for i in range(len(sections) - 1)
    )
    return {
        "passed": all(result["passed"] for result in results),
        "boundaries_checked": len(results),
        "results": results,
        "deployable": False,
    }
