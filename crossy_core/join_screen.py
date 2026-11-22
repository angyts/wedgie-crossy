"""Fail-closed screening of whole concatenated terrain sections.

A positive result is conditional on the current prototype's timing,
camera and initial-state assumptions. It is NOT compositional proof:
each joined sequence is screened from its original entry state.
"""
from .joins import join_rows
from .certification import screen_section

def screen_join(sections, **settings):
    """Validate the complete joined sequence, never individual booleans.

    Requires a grass start/end; rejects noncontiguous indices, excessive
    dangerous runs, invalid train schedules and oversized phase domains.
    Every phase is evaluated with one continuous simulation/camera clock.
    """
    rows = join_rows(sections)
    evidence = screen_section(rows, **settings)
    evidence["section_count"] = len(sections)
    evidence["row_count"] = len(rows)
    evidence["first_row"] = rows[0].index
    evidence["last_row"] = rows[-1].index
    evidence["scope"] = "whole-join-screen-not-compositional-certificate"
    return evidence
