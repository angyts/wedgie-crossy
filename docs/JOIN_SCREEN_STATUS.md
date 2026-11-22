# Whole-join fairness screening (prototype)

`screen_join` concatenates the supplied sections and calls the existing
finite-domain, camera-aware screen on the WHOLE joined sequence. It
therefore does not reset hazard phase, reaction delay, or camera time
at an internal boundary. It also rejects invalid row indices, overlong
danger runs, invalid train schedules and excessive repeat periods.

**Limitations:** This does not establish compositional certification of
arbitrary section families. It starts from a specified set of entry
columns and checks whether SOME path exists per phase; exit states are
not yet carried as a contract into arbitrary future sections. It still
uses the provisional instantaneous-move simulation and camera model.
No generated family is certified, and the runtime generator has not
been switched to screened patterns.

Next: explicit boundary state/phase contracts, generator allowlisting,
adversarial composed-world testing and real-device measurements.
