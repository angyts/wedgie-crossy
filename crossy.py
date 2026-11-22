"""Crossy hardware checkpoint 6: bounded scrolling grass world.

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

def draw_chicken(lcd, x, y):
    """Draw chicken inside the same 20-pixel tile used by tree collision."""
    x, y = x - MIN_X, y - MIN_Y
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

def draw_world(lcd, world, col, row, score):
    lcd.fill(BG)
    for screen_row in range(WINDOW):
        absolute = world.first + screen_row
        sy = (WINDOW - 1 - screen_row) * STEP
        lcd.fill_rect(0, sy, 240, STEP, BG if absolute & 1 else GRASS_ALT)
        mask = world.mask(absolute)
        for x in range(GRID_SIZE):
            if mask & (1 << x):
                tx = x * STEP
                lcd.fill_rect(tx + 8, sy + 11, 4, 7, TREE_TRUNK)
                lcd.fill_rect(tx + 3, sy + 2, 14, 12, TREE_LEAVES)
    screen_y = (WINDOW - 1 - (row - world.first)) * STEP
    # draw_chicken accepts the stage-5 logical origin offset.
    draw_chicken(lcd, MIN_X + col * STEP, MIN_Y + screen_y)
    lcd.fill_rect(0, 0, 240, 17, BG)
    lcd.text("SCORE %d" % score, 4, 4, INK)
    lcd.text("A RESET", 170, 4, INK)
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
        world = World(seed)
        col, row, score = START_COL, START_ROW, 0
        draw_world(lcd, world, col, row, score)
        debug("05 world shown, seed=%d" % seed)
        while True:
            for key in keys.pressed():
                if key == "A":
                    world = World(seed)
                    col, row, score = START_COL, START_ROW, 0
                    debug("reset score=0")
                    draw_world(lcd, world, col, row, score)
                    break
                if key in ("up", "down", "left", "right"):
                    nc, nr = move_world(world, col, row, key)
                    if (nc, nr) != (col, row):
                        col, row = nc, nr
                        if row > score:
                            score = row
                        if row - world.first > CAMERA_LEAD:
                            world.advance(row - CAMERA_LEAD)
                        debug("move %s row=%d col=%d score=%d window=%d..%d" %
                              (key, row, col, score, world.first, world.last))
                        draw_world(lcd, world, col, row, score)
                    else:
                        debug("blocked %s row=%d col=%d" % (key, row, col))
                    break
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
