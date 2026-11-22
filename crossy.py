"""Crossy hardware checkpoint 14: traffic variety and visual road cues.

Known working reference: angyts/wedgie-snake-game/snake/snake.py.
Use wedgie.py install . to launch via wedgie.json entry=run.
"""
import time
from lcd import LCD, Keys, color

DEBUG = True
FRAME_MS = 100
# Development mode never reads or writes the persistent high score.
# Switch to False for release builds after hardware validation.
DEV_MODE = True
TRAFFIC_TICKS = 3
CRASH_FRAMES = 5
CRASH_FRAME_MS = 90
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
ROAD = color(65, 68, 72)
ROAD_MARK = color(180, 175, 115)
ROAD_EDGE = color(135, 140, 135)
CAR_BLUE = color(55, 125, 220)
CAR_YELLOW = color(235, 170, 45)
CAR = color(210, 55, 45)
CAR_WINDOW = color(125, 190, 205)
CAR_WHEEL = color(25, 30, 35)
STAR = color(255, 210, 40)
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

def draw_chicken(lcd, x, y, facing="down"):
    """Draw a 20px chicken facing the last successful movement direction."""
    x, y = x - MIN_X, y - MIN_Y
    lcd.fill_rect(x + 3, y + 5, 14, 11, CHICKEN)
    lcd.fill_rect(x + 6, y + 2, 9, 6, CHICKEN)
    if facing == "left":
        lcd.fill_rect(x + 1, y + 7, 4, 3, BEAK)
        lcd.fill_rect(x + 6, y + 4, 2, 2, EYE)
    elif facing == "right":
        lcd.fill_rect(x + 15, y + 7, 4, 3, BEAK)
        lcd.fill_rect(x + 12, y + 4, 2, 2, EYE)
    elif facing == "down":
        # Front: two eyes and a centered beak.
        lcd.fill_rect(x + 7, y + 5, 2, 2, EYE)
        lcd.fill_rect(x + 12, y + 5, 2, 2, EYE)
        lcd.fill_rect(x + 9, y + 9, 3, 3, BEAK)
    else:
        # Back: a small tail, with no eyes or beak visible.
        lcd.fill_rect(x + 8, y + 1, 4, 5, CHICKEN)
        lcd.fill_rect(x + 9, y + 7, 2, 4, TREE_TRUNK)
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

def is_road(row):
    """Sparse, static test roads; no moving traffic in this checkpoint."""
    return row >= 6 and row % 12 == 6

def car_mask(seed, row):
    """Reproducible parked cars, leaving the center corridor clear."""
    if not is_road(row):
        return 0
    return ((1 << 2) | (1 << 8)) if (row // 12) % 2 == 0 else ((1 << 1) | (1 << 9))

def traffic_direction(row):
    return 1 if (row // 12) % 2 == 0 else -1

def moving_car_mask(seed, row, phase):
    """Two cars shift one cell per traffic step; wrap at the board edge."""
    base = car_mask(seed, row)
    if not base:
        return 0
    shift = (phase * traffic_direction(row)) % GRID_SIZE
    return ((base << shift) | (base >> (GRID_SIZE - shift))) & MASK_ALL if shift else base

def road_hit(seed, row, col, phase=0):
    return bool(moving_car_mask(seed, row, phase) & (1 << col))

def traffic_sweep_hit(seed, row, col, old_phase, new_phase):
    """Fail closed if traffic occupies the player's cell at either endpoint."""
    return road_hit(seed, row, col, old_phase) or road_hit(seed, row, col, new_phase)

def row_mask(seed, row):
    """Stable per-row generation; column 5 always remains clear."""
    if row < 2 or is_road(row):
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

def car_style(row):
    """Deterministic visual variant per road band."""
    return (row // 12) % 3

def car_length(row):
    return 18 if car_style(row) == 2 else 16

def traffic_interval(score):
    """Difficulty increases at scores 30 and 60, never below two ticks."""
    return max(2, TRAFFIC_TICKS - score // 30)

def draw_car(lcd, x, y, row=6):
    """Compact vehicle silhouette with windshield and wheels."""
    body = (CAR, CAR_BLUE, CAR_YELLOW)[car_style(row)]
    length = car_length(row)
    left = (STEP - length) // 2
    lcd.fill_rect(x + left, y + 5, length, 10, body)
    lcd.fill_rect(x + 5, y + 2, 10, 7, body)
    lcd.fill_rect(x + 7, y + 3, 6, 4, CAR_WINDOW)
    lcd.fill_rect(x + 4, y + 15, 4, 3, CAR_WHEEL)
    lcd.fill_rect(x + 12, y + 15, 4, 3, CAR_WHEEL)

def draw_crash_star(lcd, x, y, frame):
    """Five-frame pixel starburst, clipped to the 240px screen."""
    size = 3 + frame * 2
    cx, cy = x + 10, y + 10
    lcd.fill_rect(max(0, cx - size), cy - 2, min(240 - max(0, cx - size), size * 2), 4, STAR)
    lcd.fill_rect(cx - 2, max(0, cy - size), 4, min(240 - max(0, cy - size), size * 2), STAR)

def draw_world(lcd, world, col, row, score, best=0, paused=False, facing="right", milestone_active=False, dead=False, phase=0, crash_frame=0):
    lcd.fill(GRASS_ALT)
    for screen_row in range(WINDOW):
        absolute = world.first + screen_row
        sy = (WINDOW - 1 - screen_row) * STEP
        if is_road(absolute):
            lcd.fill_rect(0, sy, 240, STEP, ROAD)
            lcd.fill_rect(0, sy, 240, 2, ROAD_EDGE)
            lcd.fill_rect(0, sy + 18, 240, 2, ROAD_EDGE)
            for mark_x in range(0, 240, 40):
                lcd.fill_rect(mark_x + 8, sy + 9, 16, 2, ROAD_MARK)
            cars = moving_car_mask(world.seed, absolute, phase)
            for cx in range(GRID_SIZE):
                if cars & (1 << cx):
                    draw_car(lcd, cx * STEP, sy, absolute)
            continue
        mask = world.mask(absolute)
        for x in range(GRID_SIZE):
            if mask & (1 << x):
                tx = x * STEP
                lcd.fill_rect(tx + 8, sy + 11, 4, 7, TREE_TRUNK)
                lcd.fill_rect(tx + 3, sy + 2, 14, 12, TREE_LEAVES)
    screen_y = (WINDOW - 1 - (row - world.first)) * STEP
    # draw_chicken accepts the stage-5 logical origin offset.
    if dead and crash_frame:
        draw_crash_star(lcd, col * STEP, screen_y, crash_frame)
    elif not dead:
        draw_chicken(lcd, MIN_X + col * STEP, MIN_Y + screen_y, facing)
    # Minimal HUD. A tenth-row milestone briefly changes score color.
    lcd.fill_rect(0, 0, 240, 20, BG)
    score_color = CHICKEN if milestone(score) else INK
    lcd.text("SCORE %d" % score, 4, 5, score_color)
    if milestone(score):
        lcd.text("SCORE %d" % score, 5, 5, score_color)
    lcd.text("BEST %d" % best, 145, 5, INK)
    if score >= 30 and score < 33 and not dead and not paused:
        lcd.text("FASTER!", 92, 26, INK)
    if dead:
        lcd.fill_rect(8, 73, 224, 112, BG)
        lcd.text("ALWAYS LOOK", 64, 84, INK)
        lcd.text("BEFORE YOU", 68, 100, INK)
        lcd.text("CROSS THE ROAD", 49, 116, INK)
        lcd.text("YOUR SCORE: %d" % score, 57, 139, CHICKEN)
        lcd.fill_rect(48, 161, 12, 12, color(45, 205, 80))
        lcd.text("NEW RUN", 70, 163, INK)
    elif paused:
        lcd.fill_rect(38, 85, 164, 72, BG)
        lcd.text("PAUSED", 96, 95, INK)
        # Colored button icons communicate physical controls without A/B jargon.
        lcd.fill_rect(54, 117, 12, 12, color(230, 45, 55))
        lcd.text("RESUME", 76, 119, INK)
        lcd.fill_rect(54, 136, 12, 12, color(45, 205, 80))
        lcd.text("NEW RUN", 76, 138, INK)
    lcd.show()

def animate_crash(lcd, world, col, row, score, best, facing, phase):
    """Brief non-blocking-to-firmware animation with a bounded duration."""
    for frame in range(1, CRASH_FRAMES + 1):
        draw_world(lcd, world, col, row, score, best, False, facing,
                   dead=True, phase=phase, crash_frame=frame)
        time.sleep_ms(CRASH_FRAME_MS)

def run():
    import save  # Firmware-only module; host logic tests can import crossy without it.
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
        if DEV_MODE:
            best = 0
            debug("DEV MODE: best score zero; flash writes disabled")
        else:
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
        facing = "down"
        dead = False
        traffic_tick = 0
        phase = 0
        crash_animated = False
        draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
        debug("05 world shown, seed=%d" % seed)
        while True:
            # Traffic advances only during active gameplay, not while paused/dead.
            if not paused and not dead:
                traffic_tick += 1
                next_phase = traffic_tick // traffic_interval(score)
                if next_phase != phase:
                    if is_road(row) and traffic_sweep_hit(seed, row, col, phase, next_phase):
                        dead = True
                        crash_animated = False
                        debug("traffic collision row=%d col=%d" % (row, col))
                    phase = next_phase
                    if dead:
                        animate_crash(lcd, world, col, row, score, best, facing, phase)
                        crash_animated = True
                    else:
                        draw_world(lcd, world, col, row, score, best, paused, facing,
                                   dead=False, phase=phase)
            for key in keys.pressed():
                if dead:
                    if key == "A":
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        traffic_tick, phase = 0, 0
                        facing = "down"
                        dead = False
                        crash_animated = False
                        draw_world(lcd, world, col, row, score, best, False, facing, phase=phase)
                    break
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
                        if not DEV_MODE and score > saved_best:
                            try:
                                save.store("best", best)
                                saved_best = best
                            except OSError as exc:
                                debug("best save failed: %r" % (exc,))
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        traffic_tick, phase = 0, 0
                        facing = "right"
                        paused = False
                        debug("new run")
                        draw_world(lcd, world, col, row, score, best, paused, facing)
                    break
                if key in ("up", "down", "left", "right"):
                    nc, nr = move_world(world, col, row, key)
                    if (nc, nr) != (col, row):
                        col, row = nc, nr
                        facing = key
                        dead = road_hit(seed, row, col, phase)
                        if dead:
                            crash_animated = False
                        if row > score:
                            score = row
                            if score > best:
                                best = score
                        if row - world.first > CAMERA_LEAD:
                            world.advance(row - CAMERA_LEAD)
                        debug("move %s row=%d col=%d score=%d window=%d..%d" %
                              (key, row, col, score, world.first, world.last))
                        if dead:
                            debug("crash row=%d col=%d" % (row, col))
                            if not DEV_MODE and best > saved_best:
                                try:
                                    save.store("best", best)
                                    saved_best = best
                                except OSError as exc:
                                    debug("best save failed: %r" % (exc,))
                        if dead and not crash_animated:
                            animate_crash(lcd, world, col, row, score, best, facing, phase)
                            crash_animated = True
                        else:
                            draw_world(lcd, world, col, row, score, best, paused, facing, dead=dead, phase=phase)
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
