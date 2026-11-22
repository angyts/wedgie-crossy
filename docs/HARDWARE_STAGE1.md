# Hardware checkpoint 1: static chicken

Parent known-good hardware checkpoint: `1af6303` (READY screen). This commit adds only a six-rectangle pixel chicken to the same static screen. No movement, game clock, world generation, scoring, persistence, or collision logic.

Host smoke test verifies that READY and STATIC CHICKEN are drawn, exactly six rectangles stay within 240x240, a single LCD show occurs, and the idle loop polls input. Host tests do not establish device compatibility.

To verify: `git switch hardware-baseline && git pull origin hardware-baseline && python -m unittest discover -s tests -v && python wedgie.py install .`. Approve on the device. Confirm the yellow chicken is visible beneath READY and the screen stays stable. If it fails, return to `1af6303` for the last physically verified baseline.
