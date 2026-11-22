"""Crossy hardware baseline: LCD startup only, no gameplay.

Known working reference: angyts/wedgie-snake-game/snake/snake.py.
Use wedgie.py install . to launch via wedgie.json entry=run.
"""
import time
from lcd import LCD, Keys, color

DEBUG = True
FRAME_MS = 100
BG = color(22, 90, 45)
INK = color(245, 245, 230)

def debug(message):
    if DEBUG:
        print("[CROSSY BOOT]", message)

def run():
    # Match the working Snake app: initialize hardware inside run().
    debug("01 run entered")
    lcd = None
    try:
        debug("02 creating LCD")
        lcd = LCD()
        debug("03 creating Keys")
        keys = Keys()
        debug("04 drawing baseline")
        lcd.fill(BG)
        lcd.text("WEDGIE CROSSY", 48, 88, INK)
        lcd.text("BOOT BASELINE", 52, 112, INK)
        lcd.text("READY", 96, 136, INK)
        lcd.show()
        debug("05 frame shown; entering idle loop")
        while True:
            # Poll the same input API used by Snake; do not move yet.
            keys.pressed()
            time.sleep_ms(FRAME_MS)
    except Exception as exc:
        debug("ERROR: %r" % (exc,))
        import sys
        sys.print_exception(exc)
        # Best effort: show a visible error marker even if serial logs are lost.
        if lcd is not None:
            try:
                lcd.fill(0)
                lcd.text("CROSSY BOOT ERROR", 30, 110, INK)
                lcd.show()
            except Exception:
                pass
        raise
