# Moving railway physics — experimental increment

Railway geometry now models a train starting beyond either edge and
crossing the 12-column board at integer velocity. The host-only
`train_collision` checks swept overlap through one tick, including
tunneling. `warning_active` covers the ticks immediately preceding
arrival. `check_schedule` rejects a period too short for transit and
warning.

This is a standalone module, not yet integrated into `step_fp` or
`validate_fp`. The old validator_v3 whole-row train pulse remains
an approximation and should not be treated as the moving-train model.
Existing row schemas permit some schedules rejected by check_schedule;
generator parameter selection must be updated before deployment.
No fairness certification or Wedgie runtime integration is claimed.
