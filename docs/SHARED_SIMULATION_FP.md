# Fixed-point shared simulation — river integration increment

`simulation_fp.step_fp` is a new host-side transition primitive for
grass, roads and rivers. It uses the same swept-road and moving-log
primitives previously tested independently. Coordinates are integer
subtiles (256 per tile). One cardinal move occurs instantaneously at
tick start; hazards advance through the tick. A tree blocks movement,
leaving the player on the source row.

**Not production-ready:** The offline reachability search has not yet
been migrated to `step_fp`, and no Wedgie game loop uses it. Railways
raise NotImplementedError. Moving-log support is same-log and one-tick;
camera pursuit, phase-complete validation and full section certification
remain outstanding. No gameplay fairness guarantee is claimed.

Run `python -m unittest discover -s tests -v`.
