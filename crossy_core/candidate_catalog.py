"""Offline-only hazard catalog screening, NOT runtime certification.

Candidate sections are screened as complete grass-to-grass crossings.
No candidate is automatically admitted to ApprovedWorld: its existing
grass-only allowlist remains unchanged until compositional contracts exist.
"""
from .patterns import Row, GRASS, ROAD, RIVER, RAIL
from .certification import screen_section

def candidate(kind, phase=0):
    """Small reproducible fixture: safe grass, hazard, safe grass."""
    if kind == ROAD:
        middle = Row(1, ROAD, direction=1, speed=1,
                     spacing=12, length=2, phase=phase)
    elif kind == RIVER:
        middle = Row(1, RIVER, direction=1, speed=1,
                     spacing=12, length=6, phase=phase)
    elif kind == RAIL:
        middle = Row(1, RAIL, direction=1, speed=2,
                     length=3, period=30, warning=4, phase=phase)
    else:
        raise ValueError("unknown hazard family")
    return (Row(0, GRASS), middle, Row(2, GRASS))

def screen_candidate(kind, phase=0, **settings):
    rows = candidate(kind, phase)
    evidence = screen_section(rows, **settings)
    # Deliberately avoid an "approved" field: this is an offline
    # feasibility result under the prototype timing assumptions.
    evidence["family"] = kind
    evidence["candidate_phase"] = phase
    evidence["deployable"] = False
    return evidence

def screen_catalog(kinds=(ROAD, RIVER, RAIL), **settings):
    """Return evidence for each candidate; fail closed on bad parameters."""
    return tuple(screen_candidate(kind, **settings) for kind in kinds)
