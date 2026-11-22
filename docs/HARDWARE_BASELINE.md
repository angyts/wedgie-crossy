# Hardware baseline — checkpoint 0

Branch: `hardware-baseline`. The main branch remains unchanged.

## Objective
Prove that the installed Wedgie firmware calls `crossy.run()` and
renders a static frame using the same `LCD`, `Keys` and `lcd.show()`
pattern as the known-working Snake app.

The cartridge has no game loop logic, terrain generation, scoring,
persistence or moving objects. It intentionally displays **READY**.

## Diagnostics
`DEBUG = True` prints numbered `[CROSSY BOOT]` checkpoints:
01 entry, 02 LCD, 03 Keys, 04 drawing, 05 shown.
On a Python exception it prints the traceback with
`sys.print_exception`, attempts to show CROSSY BOOT ERROR, and re-raises.
The firmware may not persist prints in `log.txt`; the on-screen
READY/ERROR marker is the primary device-visible signal.

## Verification
1. `git switch hardware-baseline && git pull`
2. `python3 -m unittest discover -s tests -v`
3. `python wedgie.py install .` (approve on Wedgie)
4. Verify the screen says WEDGIE CROSSY / BOOT BASELINE / READY.
5. Report the result. Do not add movement until READY is confirmed.

Do not run `python crossy.py` on macOS: `lcd` is device-only.
No firmware update or flash erase is required. The local installer
`wedgie.py` is a development utility and is not part of the app manifest.
