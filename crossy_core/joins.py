"""Host-side section join checks; NOT a complete fairness certificate."""
from .patterns import GRASS, MAX_DANGER_RUN
from .validator_v3 import validate_multiterrain

def join_rows(sections):
    """Flatten sections, rejecting gaps and overly long danger runs.

    A section may be valid alone but fail when joined to another.
    Row indices are absolute and must be contiguous across sections.
    """
    if not sections or any(not section for section in sections):
        raise ValueError("nonempty sections required")
    rows = []
    danger = 0
    for section in sections:
        for row in section:
            if rows and row.index != rows[-1].index + 1:
                raise ValueError("noncontiguous section boundary")
            if row.kind == GRASS:
                danger = 0
            else:
                danger += 1
                if danger > MAX_DANGER_RUN:
                    raise ValueError("dangerous run crosses section limit")
            rows.append(row)
    return rows

def validate_join(sections, entry_columns=(5,), entry_phases=(0,),
                  horizon=64, reaction_ticks=0, max_wait_ticks=None):
    """Check combined sections with the v3 experimental timing model.

    This preserves temporal state across boundaries by validating one
    concatenated world, rather than independently approving sections.
    It does not prove all entry phases, train geometry or camera fairness.
    """
    rows = join_rows(sections)
    return validate_multiterrain(
        rows, entry_columns=entry_columns, entry_phases=entry_phases,
        horizon=horizon, reaction_ticks=reaction_ticks,
        max_wait_ticks=max_wait_ticks)
