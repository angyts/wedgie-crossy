"""Crossy hardware checkpoint 9: high-contrast milestones and lightweight HUD improvements.

Known working reference: angyts/wedgie-snake-game/snake/snake.py.
Use wedgie.py install . to launch via wedgie.json entry=run.
"""
import time
import save
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
TREE_TRUNK = color(105, 64, 28)
TREE_LEAVES = color(13, 65, 28)
# Fixed positions (column, row) for repeatable hardware verification.
TREES = ((6, 9), (4, 8), (2, 6), (9, 7), (8, 4), (3, 3))
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

def try_move(x, y, key):
    """Return the old position when the target tile contains a tree."""
    nx, ny = moved(x, y, key)
    col = (nx - MIN_X) // STEP
    row = (ny - 9) // STEP
    if (col, row) in TREES:
        return x, y
    return nx, ny

def draw_trees(lcd):
    for col, row in TREES:
        tx, ty = col * STEP, row * STEP
        lcd.fill_rect(tx + 8, ty + 11, 4, 7, TREE_TRUNK)
        lcd.fill_rect(tx + 3, ty + 2, 14, 12, TREE_LEAVES)

def score_for_row(best_row, y):
    """Score only new upward progress; moving down never reduces it."""
    row = (y - MIN_Y) // STEP
    return min(best_row, row)

def score_value(best_row):
    return (START_Y - (MIN_Y + best_row * STEP)) // STEP

def draw_chicken(lcd, x, y, facing="right"):
    """Draw chicken inside the same 20-pixel tile used by tree collision."""
    x, y = x - MIN_X, y - MIN_Y
    lcd.fill_rect(x + 3, y + 5, 14, 11, CHICKEN)
    lcd.fill_rect(x + 6, y + 2, 9, 6, CHICKEN)
    if facing == "left":
        lcd.fill_rect(x + 1, y + 7, 4, 3, BEAK)
        lcd.fill_rect(x + 6, y + 4, 2, 2, EYE)
    else:
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

def draw_scene(lcd, x, y, score=0):
    lcd.fill(BG)
    draw_grid(lcd)
    lcd.text("WEDGIE CROSSY", 48, 4, INK)
    lcd.text("SCORE %d" % score, 4, 20, INK)
    lcd.text("A RESET", 170, 20, INK)
    draw_trees(lcd)
    draw_chicken(lcd, x, y)
    lcd.show()

# Stage 6: bounded endless grass world, independent of the older grid helpers.
# Row 0 is the starting row; row numbers increase as the chicken goes up.
WINDOW = 12
START_COL = 5
START_ROW = 0
CAMERA_LEAD = 8
MASK_ALL = (1 << GRID_SIZE) - 1

def row_mask(seed, row):
    """Stable per-row generation; column 5 always remains clear."""
    if row < 2:
        return 0
    value = (seed ^ ((row + 1) * 0x9e3779b9)) & 0xffffffff
    value ^= value >> 16
    value = (value * 0x7feb352d) & 0xffffffff
    value ^= value >> 15
    mask = 0
    for col in range(GRID_SIZE):
        value ^= (value << 13) & 0xffffffff
        value ^= value >> 17
        value ^= (value << 5) & 0xffffffff
        value &= 0xffffffff
        if col != START_COL and value % 7 == 0:
            mask |= 1 << col
    return mask & MASK_ALL

class World:
    def __init__(self, seed):
        self.seed = seed
        self.rows = [0] * WINDOW
        self.first = 0
        self.last = WINDOW - 1
        for row in range(WINDOW):
            self.rows[row] = row_mask(seed, row)

    def mask(self, row):
        if row < self.first or row > self.last:
            return None
        return self.rows[row % WINDOW]

    def advance(self, new_first):
        if new_first < self.first:
            raise ValueError("world cannot scroll backward")
        while self.first < new_first:
            self.first += 1
            self.last += 1
            self.rows[self.last % WINDOW] = row_mask(self.seed, self.last)

def move_world(world, col, row, direction):
    dc, dr = 0, 0
    if direction == "left":
        dc = -1
    elif direction == "right":
        dc = 1
    elif direction == "up":
        dr = 1
    elif direction == "down":
        dr = -1
    else:
        return col, row
    nc, nr = col + dc, row + dr
    if not 0 <= nc < GRID_SIZE or nr < world.first:
        return col, row
    mask = world.mask(nr)
    if mask is None or mask & (1 << nc):
        return col, row
    return nc, nr

def milestone(score):
    return score if score > 0 and score % 10 == 0 else 0

def draw_world(lcd, world, col, row, score, best=0, paused=False, facing="right", milestone_active=False):
    lcd.fill(GRASS_ALT)
    for screen_row in range(WINDOW):
        absolute = world.first + screen_row
        sy = (WINDOW - 1 - screen_row) * STEP
        mask = world.mask(absolute)
        for x in range(GRID_SIZE):
            if mask & (1 << x):
                tx = x * STEP
                lcd.fill_rect(tx + 8, sy + 11, 4, 7, TREE_TRUNK)
                lcd.fill_rect(tx + 3, sy + 2, 14, 12, TREE_LEAVES)
    screen_y = (WINDOW - 1 - (row - world.first)) * STEP
    # draw_chicken accepts the stage-5 logical origin offset.
    draw_chicken(lcd, MIN_X + col * STEP, MIN_Y + screen_y, facing)
    # Clear, legible HUD: no center-screen milestone interruption.
    lcd.fill_rect(0, 0, 240, 24, BG)
    score_text = str(score)
    if milestone_active:
        # Built-in 8px font: double-print with a 1px offset for bold effect.
        lcd.text(score_text, 4, 4, CHICKEN)
        lcd.text(score_text, 5, 4, CHICKEN)
        lcd.text("x10", 4 + len(score_text) * 8 + 10, 4, CHICKEN)
    else:
        lcd.text(score_text, 4, 4, INK)
    # Feature 1: subtle ten-row progress bar along the bottom of the HUD.
    lcd.fill_rect(0, 21, (score % 10) * 24, 2, CHICKEN)
    # Feature 2: highlight the best score only when this run matches it.
    best_color = CHICKEN if score > 0 and score == best else INK
    lcd.text("BEST %d" % best, 125, 4, best_color)
    # Feature 3: on-screen pause affordance without a reset label.
    if not paused:
        lcd.text("Y", 224, 13, INK)
    if paused:
        lcd.fill_rect(38, 85, 164, 72, BG)
        lcd.text("PAUSED", 96, 95, INK)
        lcd.text("B RESUME", 78, 114, INK)
        lcd.text("A NEW RUN", 74, 133, INK)
    lcd.show()

def run():
    debug("01 run entered")
    lcd = None
    try:
        debug("02 creating LCD")
        lcd = LCD()
        debug("03 creating Keys")
        keys = Keys()
        debug("04 creating bounded grass world")
        # Fixed seed during hardware bring-up: every reset is reproducible.
        seed = 0x13579bdf
        try:
            best = save.load("best", 0)
            if not isinstance(best, int) or best < 0:
                best = 0
        except (OSError, ValueError, TypeError) as exc:
            debug("best load failed: %r" % (exc,))
            best = 0
        saved_best = best
        world = World(seed)
        col, row, score = START_COL, START_ROW, 0
        paused = False
        facing = "right"
        milestone_until = None
        draw_world(lcd, world, col, row, score, best, paused, facing)
        debug("05 world shown, seed=%d" % seed)
        while True:
            for key in keys.pressed():
                if key == "Y" and not paused:
                    paused = True
                    debug("paused")
                    draw_world(lcd, world, col, row, score, best, paused, facing)
                    break
                if paused:
                    if key in ("B", "Y"):
                        paused = False
                        debug("resumed")
                        draw_world(lcd, world, col, row, score, best, paused, facing)
                    elif key == "A":
                        if score > saved_best:
                            try:
                                save.store("best", best)
                                saved_best = best
                            except OSError as exc:
                                debug("best save failed: %r" % (exc,))
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        facing = "right"
                        milestone_until = None
                        paused = False
                        debug("new run")
                        draw_world(lcd, world, col, row, score, best, paused, facing)
                    break
                if key in ("up", "down", "left", "right"):
                    nc, nr = move_world(world, col, row, key)
                    if (nc, nr) != (col, row):
                        col, row = nc, nr
                        if key in ("left", "right"):
                            facing = key
                        if row > score:
                            score = row
                            if milestone(score):
                                milestone_until = time.ticks_add(time.ticks_ms(), 900)
                            if score > best:
                                best = score
                            if milestone(score) and best > saved_best:
                                try:
                                    save.store("best", best)
                                    saved_best = best
                                except OSError as exc:
                                    debug("best save failed: %r" % (exc,))
                        if row - world.first > CAMERA_LEAD:
                            world.advance(row - CAMERA_LEAD)
                        debug("move %s row=%d col=%d score=%d window=%d..%d" %
                              (key, row, col, score, world.first, world.last))
                        draw_world(lcd, world, col, row, score, best, paused, facing,
                                   milestone_until is not None)
                    else:
                        debug("blocked %s row=%d col=%d" % (key, row, col))
                    break
            if milestone_until is not None and time.ticks_diff(
                    time.ticks_ms(), milestone_until) >= 0:
                milestone_until = None
                if not paused:
                    draw_world(lcd, world, col, row, score, best, paused, facing)
            time.sleep_ms(FRAME_MS)
    except Exception as exc:
        debug("ERROR: %r" % (exc,))
        import sys
        sys.print_exception(exc)
        if lcd is not None:
            try:
                lcd.fill(0)
                lcd.text("CROSSY BOOT ERROR", 30, 110, INK)
                lcd.show()
            except Exception:
                pass
        raise
