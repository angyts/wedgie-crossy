# Shared railway integration (experimental)

The fixed-point simulation and reachability validator now both call the
moving-train geometry in railway.py. A warning blocks entry into a rail
row; a train collision kills the player, including swept motion within
a tick. Remaining on a rail row during a warning is allowed if clear.

The model still uses instantaneous player moves at tick boundaries and
finite sampled entry phases. The generator does not yet enforce valid
rail schedules, camera pursuit is missing, and no terrain families have
been certified. Do not ship as a fairness guarantee.

Run: python -m unittest discover -s tests -v
