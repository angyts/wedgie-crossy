"""Bounded adversarial audit of mixed hazard sequences, offline only.

This tool enumerates candidate combinations and screens the entire
joined world, preserving absolute hazard time and camera state.
It never grants runtime approval. Results are conditional on the
existing prototype simulation and entry-state assumptions.
"""
from .patterns import GRASS, ROAD, RIVER, RAIL, Row
from .adversarial import sweep_join

FAMILIES = (ROAD, RIVER, RAIL)

def hazard_row(index, kind):
    if kind == ROAD:
        return Row(index, ROAD, direction=1, speed=1, spacing=12,
                   length=2, phase=0)
    if kind == RIVER:
        return Row(index, RIVER, direction=1, speed=1, spacing=12,
                   length=6, phase=3)
    if kind == RAIL:
        return Row(index, RAIL, direction=1, speed=2,
                   length=3, period=30, warning=4, phase=0)
    raise ValueError("unknown hazard")

def mixed_sections(kinds):
    """Each section starts with grass; final section ends with grass."""
    if not kinds or len(kinds) > 4:
        raise ValueError("1..4 hazards required")
    sections = []
    index = 0
    for kind in kinds:
        sections.append((Row(index, GRASS), hazard_row(index + 1, kind)))
        index += 2
    sections.append((Row(index, GRASS),))
    return tuple(sections)

def audit_mixed(kinds, max_cases=27, **settings):
    """Enumerate all ordered sequences of length kinds (1..3).

    Reports failures and oversized phase domains as rejected cases.
    No case is deployable regardless of the diagnostic outcome.
    """
    if type(kinds) is not int or not 1 <= kinds <= 3:
        raise ValueError("kinds must be 1..3")
    total = len(FAMILIES) ** kinds
    if type(max_cases) is not int or max_cases < total:
        raise ValueError("case cap exceeded")
    cases = []
    for code in range(total):
        value = code
        family = []
        for _ in range(kinds):
            family.append(FAMILIES[value % len(FAMILIES)])
            value //= len(FAMILIES)
        try:
            evidence = sweep_join(mixed_sections(family), **settings)
            passed = evidence["passed"]
            phases = evidence["phases_checked"]
            failures = evidence["failing_phases"]
            reason = None
        except ValueError as exc:
            passed, phases, failures = False, 0, ()
            reason = str(exc)
        cases.append({"families": tuple(family), "passed": passed,
                      "phases_checked": phases, "failing_phases": failures,
                      "rejection": reason, "deployable": False})
    return tuple(cases)
