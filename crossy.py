"""Crossy hardware checkpoint 3: visible grass grid and aligned movement.

Known working reference: angyts/wedgie-snake-game/snake/snake.py.
Use wedgie.py install . to launch via wedgie.json entry=run.
"""
import time
from lcd import LCD, Keys, color

DEBUG = True
FRAME_MS = 100
BG = color(22, 90, 45)
INK = color(245, 245, 230)
CHICKEN = color(255, 215, 70)
BEAK = color(245, 120, 40)
EYE = color(18, 25, 20)
STEP = 20
GRID_SIZE = 12
GRASS_ALT = color(27, 105, 53)
START_X = 110
START_Y = 189
MIN_X, MAX_X = 10, 210
MIN_Y, MAX_Y = 9, 209

def moved(x, y, key):
    """Pure one-press movement; keep the whole chicken inside the screen."""
    if key == "left":
        x -= STEP
    elif key == "right":
        x += STEP
    elif key == "up":
        y -= STEP
    elif key == "down":
        y += STEP
    return max(MIN_X, min(MAX_X, x)), max(MIN_Y, min(MAX_Y, y))

def draw_chicken(lcd, x, y):
    """Compact chicken centered in one 20-pixel grass tile."""
    lcd.fill_rect(x + 3, y + 5, 14, 11, CHICKEN)
    lcd.fill_rect(x + 6, y + 2, 9, 6, CHICKEN)
    lcd.fill_rect(x + 15, y + 7, 4, 3, BEAK)
    lcd.fill_rect(x + 12, y + 4, 2, 2, EYE)
    lcd.fill_rect(x + 5, y + 16, 2, 3, BEAK)
    lcd.fill_rect(x + 13, y + 16, 2, 3, BEAK)

def draw_grid(lcd):
    """12 by 12 alternating grass tiles, no hazards."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (row + col) & 1:
                lcd.fill_rect(col * STEP, row * STEP, STEP, STEP, GRASS_ALT)

def debug(message):
    if DEBUG:
        print("[CROSSY BOOT]", message)

def draw_scene(lcd, x, y):
    lcd.fill(BG)
    draw_grid(lcd)
    lcd.text("WEDGIE CROSSY", 48, 4, INK)
    lcd.text("GRID TEST", 80, 16, INK)
    draw_chicken(lcd, x, y)
    lcd.show()

def run():
    # Match the working Snake app: initialize hardware inside run().
    debug("01 run entered")
    lcd = None
    try:
        debug("02 creating LCD")
        lcd = LCD()
        debug("03 creating Keys")
        keys = Keys()
        debug("04 drawing 12x12 grass grid")
        x, y = START_X, START_Y
        draw_scene(lcd, x, y)
        debug("05 frame shown; polling directional presses")
        while True:
            for key in keys.pressed():
                if key in ("up", "down", "left", "right"):
                    next_x, next_y = moved(x, y, key)
                    if (next_x, next_y) != (x, y):
                        x, y = next_x, next_y
                        debug("move %s -> %d,%d" % (key, x, y))
                        draw_scene(lcd, x, y)
                    break
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
