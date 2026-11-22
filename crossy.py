"""Crossy hardware checkpoint 14: traffic variety and visual road cues.

Known working reference: angyts/wedgie-snake-game/snake/snake.py.
Use wedgie.py install . to launch via wedgie.json entry=run.
"""
import time
try:
    import gc
except ImportError:
    gc = None
import crossy_worldgen as worldgen
from lcd import LCD, Keys, color

DEBUG = True
PROFILE_RENDER = False
_render_frames = 0
_render_total_ms = 0
_render_max_ms = 0
_debug_last_ms = None
_debug_fps = 0
# Integration gate: preserve known-good hardware behavior until validation.
PROCEDURAL_WORLD = True
# Set to an integer to reproduce a world; None uses timing-derived seeds.
FIXED_SEED = None
FRAME_MS = 100
# Development mode never reads or writes the persistent high score.
# Switch to False for release builds after hardware validation.
DEV_MODE = True
TRAFFIC_TICKS = 3
SMOOTH_TRAFFIC = True  # Set False if LCD transfers are too slow.
SMOOTH_STEPS = (5, 10, 15)  # Maximum intermediate positions.
SMOOTH_BUDGET_MS = 65  # Skip late cosmetic frames; never delay controls.
SMOOTH_TRAFFIC = False
# One intermediate visual frame; logical collisions remain grid-based.
# Maximum one grid-cell advance per traffic update, independent of FPS.
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
WATER = color(35, 105, 175)
SPLASH = color(215, 240, 255)
LOG = color(130, 83, 42)
LOG_GRAIN = color(165, 111, 62)
LOG_DARK = color(88, 53, 30)
LOG_HIGHLIGHT = color(185, 132, 76)
LILY = color(45, 165, 70)
LILY_VEIN = color(110, 205, 95)
LILY_DARK = color(23, 100, 45)
LILY_LIGHT = color(85, 195, 95)
WATER_RIPPLE = color(65, 135, 195)
TREE_HIGHLIGHT = color(28, 90, 38)
SHOULDER = color(95, 105, 75)
FLOWER = color(240, 205, 100)
GRASS_PATCH = color(35, 118, 60)
PEBBLE = color(135, 150, 120)
TREE_LIGHT = color(48, 133, 56)
TREE_PINE = color(17, 84, 45)
TREE_BUSH = color(42, 112, 38)
FLOWER_PINK = color(240, 115, 165)
FLOWER_WHITE = color(242, 232, 210)
FLOWER_BLUE = color(130, 175, 240)
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
CAMERA_LEAD = 5  # Player settles near the screen center.
MASK_ALL = (1 << GRID_SIZE) - 1

def terrain_kind(seed, row):
    if PROCEDURAL_WORLD:
        return worldgen.section(seed, row)[0]
    if is_river(row):
        return river_type(row)
    if is_road(row):
        return "road"
    return "grass"

def generated_mask(seed, row, phase):
    kind = terrain_kind(seed, row)
    if kind == "road":
        return worldgen.road_mask(seed, row, phase) if PROCEDURAL_WORLD else moving_car_mask(seed, row, phase)
    if kind == "logs":
        return worldgen.log_mask(seed, row, phase) if PROCEDURAL_WORLD else log_mask(row, phase)
    if kind == "lilies":
        return worldgen.lily_mask(seed, row) if PROCEDURAL_WORLD else lily_mask(row)
    return 0

def generated_trees(seed, row):
    return worldgen.tree_mask(seed, row) if PROCEDURAL_WORLD else row_mask(seed, row)

def new_run_seed(ticks):
    if not PROCEDURAL_WORLD:
        return 0x13579bdf
    if FIXED_SEED is not None:
        return FIXED_SEED & 0xffffffff
    return worldgen.seed_from_ticks(ticks)

def hazard_at(seed, row, col, phase):
    """Collision uses the exact same mask as the renderer."""
    kind = terrain_kind(seed, row)
    if kind == "road":
        return bool(generated_mask(seed, row, phase) & (1 << col))
    if kind in ("logs", "lilies"):
        return not bool(generated_mask(seed, row, phase) & (1 << col))
    return bool(generated_trees(seed, row) & (1 << col))

def generated_traffic_hit(seed, row, col, before, after):
    return (hazard_at(seed, row, col, before) or
            hazard_at(seed, row, col, after))

def generated_move(world, col, row, direction, phase):
    """Apply movement and terrain safety consistently with procedural render."""
    dc, dr = 0, 0
    if direction == "up": dr = 1
    elif direction == "down": dr = -1
    elif direction == "left": dc = -1
    elif direction == "right": dc = 1
    else: return col, row, False
    nc, nr = col + dc, row + dr
    if not 0 <= nc < GRID_SIZE or nr < world.first or nr > world.last:
        return col, row, False
    if terrain_kind(world.seed, nr) == "grass" and hazard_at(world.seed, nr, nc, phase):
        return col, row, False
    return nc, nr, hazard_at(world.seed, nr, nc, phase)

def generated_carry(seed, row, col):
    kind, lane, width = worldgen.section(seed, row)
    if kind != "logs":
        return col
    new_col = col + worldgen.log_direction(seed, row)
    return new_col if 0 <= new_col < GRID_SIZE else None

def is_river(row):
    """Sparse river rows, separated from roads."""
    return row >= 12 and row % 24 == 12

def river_type(row):
    """Alternating river styles: first logs, second lily pads."""
    if not is_river(row):
        return None
    return "logs" if (row // 24) % 2 == 0 else "lilies"

def lily_mask(row):
    """Single stationary lily pad on selected river rows."""
    if river_type(row) != "lilies":
        return 0
    return 1 << START_COL

def on_lily(row, col):
    return bool(lily_mask(row) & (1 << col))

def water_supported(row, col, phase):
    return on_lily(row, col) or supported_by_log(row, col, phase)

def log_mask(row, phase):
    """Two three-cell logs; positions wrap at the edges."""
    if river_type(row) != "logs":
        return 0
    shift = (phase * (-1 if (row // 24) & 1 else 1)) % GRID_SIZE
    mask = 0
    for start in (1, 7):
        for i in range(3):
            mask |= 1 << ((start + i + shift) % GRID_SIZE)
    return mask

def supported_by_log(row, col, phase):
    return bool(log_mask(row, phase) & (1 << col))

def carry_on_log(row, col, phase):
    """Carry one tile; returning None indicates off-screen drift."""
    direction = -1 if (row // 24) & 1 else 1
    new_col = col + direction
    if new_col < 0 or new_col >= GRID_SIZE:
        return None
    return new_col

def is_road(row):
    """Sparse, static test roads; no moving traffic in this checkpoint."""
    return row >= 6 and (row % 12 == 6 or (row >= 42 and row % 12 == 7))

def car_mask(seed, row):
    """Reproducible parked cars, leaving the center corridor clear."""
    if not is_road(row):
        return 0
    return ((1 << 2) | (1 << 8)) if (row // 12) % 2 == 0 else ((1 << 1) | (1 << 9))

def traffic_direction(row):
    return (1 if (row // 12) % 2 == 0 else -1) * (-1 if row % 12 == 7 else 1)

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
    if row < 2 or is_road(row) or is_river(row):
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
            self.rows[row] = generated_trees(seed, row)

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
            self.rows[self.last % WINDOW] = generated_trees(self.seed, self.last)

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

def car_color(row, col, phase=0, seed=None):
    """Color follows the vehicle from its original column, including wraps."""
    if PROCEDURAL_WORLD and seed is not None:
        origin = (col - worldgen.road_position(seed, row, phase)) % GRID_SIZE
        return (CAR, CAR_BLUE, CAR_YELLOW)[(worldgen.mix32(seed ^ row) + origin // 3) % 3]
    origin = (col - phase * traffic_direction(row)) % GRID_SIZE
    return (CAR, CAR_BLUE, CAR_YELLOW)[(row // 12 + origin // 3) % 3]

def car_style(row):
    """Deterministic visual variant per road band."""
    return (row // 12) % 3

def car_length(row):
    return 18 if car_style(row) == 2 else 16

def next_traffic_phase(phase):
    """Never recompute absolute phase from score-dependent intervals."""
    return phase + 1

def traffic_due(now, deadline):
    return time.ticks_diff(now, deadline) >= 0

def traffic_interval(score):
    """Difficulty increases at scores 30 and 60, never below two ticks."""
    return max(2, TRAFFIC_TICKS - score // 30)

def draw_splash(lcd, x, y, frame):
    """Expanding pixel rings; fixed number of bounded rectangles."""
    cx, cy = x + 10, y + 10
    radius = 2 + frame * 2
    left = max(0, cx - radius)
    right = min(240, cx + radius)
    top = max(0, cy - radius)
    bottom = min(240, cy + radius)
    if right > left and bottom > top:
        lcd.fill_rect(left, top, right - left, 2, SPLASH)
        lcd.fill_rect(left, bottom - 2, right - left, 2, SPLASH)
        lcd.fill_rect(left, top, 2, bottom - top, SPLASH)
        lcd.fill_rect(right - 2, top, 2, bottom - top, SPLASH)

def draw_lily(lcd, x, y):
    """Rounded 20x20 lily leaf with a notch and veins, no heap allocations."""
    # Staggered horizontal bands approximate a circular leaf silhouette.
    lcd.fill_rect(x + 6, y + 1, 8, 18, LILY_DARK)
    lcd.fill_rect(x + 3, y + 4, 14, 12, LILY_DARK)
    lcd.fill_rect(x + 1, y + 7, 18, 6, LILY_DARK)
    lcd.fill_rect(x + 6, y + 3, 8, 14, LILY)
    lcd.fill_rect(x + 4, y + 6, 12, 8, LILY)
    lcd.fill_rect(x + 7, y + 5, 5, 4, LILY_LIGHT)
    # Open V-shaped notch at the top edge.
    lcd.fill_rect(x + 9, y + 1, 2, 4, WATER)
    lcd.fill_rect(x + 8, y + 1, 1, 2, WATER)
    lcd.fill_rect(x + 11, y + 1, 1, 2, WATER)
    # Central vein and two small branches.
    lcd.fill_rect(x + 9, y + 7, 2, 9, LILY_VEIN)
    lcd.fill_rect(x + 6, y + 10, 3, 1, LILY_VEIN)
    lcd.fill_rect(x + 11, y + 12, 3, 1, LILY_VEIN)

def draw_car(lcd, x, y, row=6, phase=0, seed=None, identity_col=None):
    """Compact vehicle silhouette with windshield and wheels."""
    body = car_color(row, x // STEP if identity_col is None else identity_col, phase, seed)
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

def draw_tree(lcd, x, y, variant):
    """Three 20px obstacle silhouettes; geometry never changes collisions."""
    lcd.fill_rect(x + 8, y + 12, 4, 6, TREE_TRUNK)
    if variant == 0:
        lcd.fill_rect(x + 5, y + 2, 10, 14, TREE_LEAVES)
        lcd.fill_rect(x + 2, y + 6, 16, 7, TREE_LEAVES)
        lcd.fill_rect(x + 6, y + 4, 6, 4, TREE_LIGHT)
    elif variant == 1:
        lcd.fill_rect(x + 8, y + 1, 4, 15, TREE_PINE)
        lcd.fill_rect(x + 5, y + 5, 10, 10, TREE_PINE)
        lcd.fill_rect(x + 2, y + 11, 16, 5, TREE_PINE)
        lcd.fill_rect(x + 8, y + 4, 3, 5, TREE_LIGHT)
    else:
        lcd.fill_rect(x + 2, y + 7, 8, 9, TREE_BUSH)
        lcd.fill_rect(x + 10, y + 6, 8, 10, TREE_BUSH)
        lcd.fill_rect(x + 6, y + 2, 9, 11, TREE_LEAVES)
        lcd.fill_rect(x + 9, y + 4, 4, 3, TREE_LIGHT)

def draw_flower(lcd, x, y, variant):
    petals = (FLOWER_PINK, FLOWER_WHITE, FLOWER_BLUE)[variant % 3]
    lcd.fill_rect(x + 9, y + 11, 2, 5, TREE_HIGHLIGHT)
    lcd.fill_rect(x + 7, y + 7, 6, 2, petals)
    lcd.fill_rect(x + 9, y + 5, 2, 6, petals)
    lcd.fill_rect(x + 9, y + 8, 2, 2, FLOWER)

def draw_log_runs(lcd, mask, sy):
    """Draw continuous visible log spans; screen-edge wraps are separate spans."""
    col = 0
    while col < GRID_SIZE:
        if not (mask & (1 << col)):
            col += 1
            continue
        first = col
        while col + 1 < GRID_SIZE and mask & (1 << (col + 1)):
            col += 1
        last = col
        left = first * STEP
        width = (last - first + 1) * STEP
        # One unbroken bark silhouette across all occupied cells.
        lcd.fill_rect(left, sy + 5, width, 12, LOG_DARK)
        lcd.fill_rect(left + 1, sy + 6, width - 2, 10, LOG)
        lcd.fill_rect(left + 3, sy + 7, width - 6, 2, LOG_HIGHLIGHT)
        lcd.fill_rect(left + 4, sy + 12, width - 8, 1, LOG_GRAIN)
        # End-grain rings only at visible ends, not every grid cell.
        lcd.fill_rect(left + 2, sy + 9, 2, 4, LOG_GRAIN)
        lcd.fill_rect(left + width - 4, sy + 9, 2, 4, LOG_GRAIN)
        col += 1

def draw_debug_overlay(lcd, seed, phase):
    """Development-only seed, measured draw FPS, free heap and traffic phase."""
    global _debug_last_ms, _debug_fps
    if not DEBUG:
        return
    now = time.ticks_ms() if hasattr(time, "ticks_ms") else None
    if now is not None and _debug_last_ms is not None:
        elapsed = time.ticks_diff(now, _debug_last_ms) if hasattr(time, "ticks_diff") else now - _debug_last_ms
        if elapsed > 0:
            sample = min(99, 1000 // elapsed)
            _debug_fps = sample if _debug_fps == 0 else (_debug_fps * 3 + sample) // 4
    if now is not None:
        _debug_last_ms = now
    free_kb = -1
    if gc is not None and hasattr(gc, "mem_free"):
        free_kb = gc.mem_free() // 1024
    lcd.fill_rect(0, 20, 240, 14, BG)
    lcd.text("S:%08X F:%d M:%dK P:%d" %
             (seed & 0xffffffff, _debug_fps, free_kb, phase % 100), 1, 22, INK)

def draw_dead_chicken(lcd, kind, frame):
    """Death animation contained in the y=44..111 scene above the popup."""
    x, y = 120, 64
    if kind == "road":
        # Exaggerated squash: the body spreads and becomes almost flat.
        height = max(3, 28 - frame * 6)
        width = 32 + frame * 7
        top = y + 31 - height
        lcd.fill_rect(x - width // 2, top, width, height, CHICKEN)
        lcd.fill_rect(x + width // 2, top + height // 2, 7, 3, BEAK)
        lcd.fill_rect(x - 12, top + 1, 3, 2, EYE)
        lcd.fill_rect(x + 10, top + 1, 3, 2, EYE)
        lcd.fill_rect(x - 40, y + 32, 80, 3, ROAD_EDGE)
        # A compact car rolls over the chicken: body, window, and a large wheel.
        car_x = x - 72 + min(frame, 5) * 16
        lcd.fill_rect(car_x, y - 10, 62, 18, CAR)
        lcd.fill_rect(car_x + 12, y - 18, 32, 10, CAR)
        lcd.fill_rect(car_x + 17, y - 16, 21, 7, CAR_WINDOW)
        # Both axles are visible; the rear wheel follows the front.
        for wheel_x in (car_x + 2, car_x + 33):
            lcd.fill_rect(wheel_x, y + 2, 27, 29, CAR_WHEEL)
            lcd.fill_rect(wheel_x + 4, y + 6, 19, 21, ROAD_EDGE)
            lcd.fill_rect(wheel_x + 10, y + 12, 7, 8, CAR_WHEEL)
    else:
        # Waterline rises, the chicken sinks, and bubbles escape upward.
        water_top = y + 31 - min(frame, 5) * 5
        depth = min(18, frame * 4)
        visible = max(5, 27 - depth)
        lcd.fill_rect(x - 16, y + depth, 32, visible, CHICKEN)
        lcd.fill_rect(x + 16, y + depth + 5, 8, 4, BEAK)
        lcd.fill_rect(x + 7, y + depth + 4, 3, 3, EYE)
        lcd.fill_rect(x - 40, water_top, 80, y + 35 - water_top, WATER)
        lcd.fill_rect(x - 38, water_top, 76, 2, WATER_RIPPLE)
        # Two bubble trails drift upward with staggered timing.
        for bubble in range(3):
            bx = x + 12 + (bubble % 2) * 9
            by = y + 22 - ((frame * 5 + bubble * 9) % 25)
            lcd.fill_rect(bx, by, 3 + (bubble & 1), 3 + (bubble & 1), SPLASH)

def changed_hazard_rows(world, old_phase, new_phase, player_row):
    rows = [player_row]
    for index in range(WINDOW):
        absolute = world.first + index
        if absolute != player_row and terrain_kind(world.seed, absolute) in ("road", "logs"):
            if generated_mask(world.seed, absolute, old_phase) != generated_mask(world.seed, absolute, new_phase):
                rows.append(absolute)
    return rows

def dynamic_rows(world, player_row):
    """Small fixed-size dirty row list; no persistent framebuffer copy."""
    rows = [player_row]
    for index in range(WINDOW):
        absolute = world.first + index
        kind = terrain_kind(world.seed, absolute)
        if kind == "road" or kind == "logs":
            if absolute != player_row:
                rows.append(absolute)
    return rows

class ClippedLCD:
    """Small draw-only adapter clipping translated sprites to a lane."""
    def __init__(self, lcd, dx, y, height):
        self.lcd = lcd
        self.dx = dx
        self.y = y
        self.bottom = y + height

    def fill_rect(self, x, y, w, h, ink):
        x += self.dx
        left = max(0, x)
        right = min(240, x + w)
        top = max(self.y, y)
        bottom = min(self.bottom, y + h)
        if left < right and top < bottom:
            self.lcd.fill_rect(left, top, right - left, bottom - top, ink)

def interpolation_steps(now, started, budget_ms=SMOOTH_BUDGET_MS):
    """Choose a bounded visual offset without waiting for the LCD.

    On slow hardware, jump to the latest useful offset instead of trying
    to render overdue intermediate frames. This does not advance physics.
    """
    elapsed = time.ticks_diff(now, started) if hasattr(time, "ticks_diff") else now - started
    if elapsed < 0:
        elapsed = 0
    if elapsed >= budget_ms:
        return 20
    return min(19, (elapsed * 20) // budget_ms)

def preview_traffic(lcd, world, old_phase, new_phase, player_row, keys):
    """Three sub-tile frames, transferring only changed sprite footprints.

    Physics and collision masks remain at integer phases. Returns a buffered
    key if a press arrives during animation.
    """
    # Input must be captured even when cosmetic rendering is disabled.
    pressed = keys.pressed()
    if pressed:
        return pressed[0]
    if not SMOOTH_TRAFFIC or not hasattr(lcd, "show_rect"):
        return None
    pending = None
    started = time.ticks_ms() if hasattr(time, "ticks_ms") else None
    previous_step = 0
    for target_step in SMOOTH_STEPS:
        pressed = keys.pressed()
        if pressed:
            return pressed[0]
        if started is None:
            step = target_step
        else:
            # Time-based pacing: skip intermediate frames already made late
            # by previous SPI transfers instead of extending the animation.
            elapsed = time.ticks_diff(time.ticks_ms(), started)
            if elapsed >= SMOOTH_BUDGET_MS:
                break
            step = max(target_step, interpolation_steps(time.ticks_ms(), started))
        if step <= previous_step or step >= STEP:
            continue
        previous_step = step
        for index in range(WINDOW):
            absolute = world.first + index
            kind = terrain_kind(world.seed, absolute)
            if kind not in ("road", "logs") or absolute == player_row:
                continue
            old_mask = generated_mask(world.seed, absolute, old_phase)
            new_mask = generated_mask(world.seed, absolute, new_phase)
            if old_mask == new_mask:
                continue
            if pending is None:
                pressed = keys.pressed()
                if pressed:
                    # Prioritize the player's input over cosmetic animation.
                    return pressed[0]
            sy = (WINDOW - 1 - index) * STEP
            # Rebuild the underlying lane in framebuffer, but send only
            # old/new sprite footprints plus their one-cell margin.
            if kind == "road":
                lcd.fill_rect(0, sy, 240, STEP, ROAD)
                lcd.fill_rect(0, sy, 240, 2, ROAD_EDGE)
                lcd.fill_rect(0, sy + 18, 240, 2, ROAD_EDGE)
                lcd.fill_rect(0, sy + 2, 240, 1, SHOULDER)
                lcd.fill_rect(0, sy + 17, 240, 1, SHOULDER)
                stripe_shift = (worldgen.mix32(world.seed ^ absolute) & 1) * 8
                for mark_x in range(0, 240, 40):
                    mx = mark_x + 8 + stripe_shift
                    if mx + 16 <= 240:
                        lcd.fill_rect(mx, sy + 9, 16, 2, ROAD_MARK)
                direction = worldgen.road_direction(world.seed, absolute)
                for cx in range(GRID_SIZE):
                    if old_mask & (1 << cx):
                        for wrap in (-240, 0, 240):
                            px = cx * STEP + direction * step + wrap
                            if -STEP < px < 240:
                                draw_car(ClippedLCD(lcd, 0, sy, STEP), px, sy,
                                         absolute, old_phase, world.seed, identity_col=cx)
            else:
                lcd.fill_rect(0, sy, 240, STEP, WATER)
                for rx in range((absolute % 3) * 12, 240, 60):
                    lcd.fill_rect(rx, sy + 3, 10, 1, WATER_RIPPLE)
                direction = worldgen.log_direction(world.seed, absolute)
                # Draw connected trunks through translated, clipped spans.
                for wrap in (-240, 0, 240):
                    draw_log_runs(ClippedLCD(lcd, direction * step + wrap, sy, STEP),
                                  old_mask, sy)
            # Expand the old/new occupancy by one tile for intermediate pixels.
            mask = old_mask | new_mask
            mask |= (mask << 1) | (mask >> 1)
            mask &= MASK_ALL
            cx = 0
            while cx < GRID_SIZE:
                if not (mask & (1 << cx)):
                    cx += 1
                    continue
                first = cx
                while cx + 1 < GRID_SIZE and (mask & (1 << (cx + 1))):
                    cx += 1
                lcd.show_rect(first * STEP, sy, (cx - first + 1) * STEP, STEP)
                cx += 1
    return pending

def draw_world(lcd, world, col, row, score, best=0, paused=False, facing="right", milestone_active=False, dead=False, phase=0, crash_frame=0, water_frame=0, death_kind=None, chicken_dx=0, dirty_rows=None, previous_phase=None):
    global _render_frames, _render_total_ms, _render_max_ms
    render_started = time.ticks_ms() if PROFILE_RENDER else 0
    if dirty_rows is None:
        lcd.fill(GRASS_ALT)
    for screen_row in range(WINDOW):
        absolute = world.first + screen_row
        sy = (WINDOW - 1 - screen_row) * STEP
        if dirty_rows is not None and absolute not in dirty_rows:
            continue
        if dirty_rows is not None:
            lcd.fill_rect(0, sy, 240, STEP, GRASS_ALT)
        kind = terrain_kind(world.seed, absolute)
        if kind in ("logs", "lilies"):
            lcd.fill_rect(0, sy, 240, STEP, WATER)
            for rx in range((absolute % 3) * 12, 240, 60):
                lcd.fill_rect(rx, sy + 3, 10, 1, WATER_RIPPLE)
            pads = generated_mask(world.seed, absolute, phase) if kind == "lilies" else 0
            for px in range(GRID_SIZE):
                if pads & (1 << px):
                    draw_lily(lcd, px * STEP, sy)
            logs = generated_mask(world.seed, absolute, phase) if kind == "logs" else 0
            draw_log_runs(lcd, logs, sy)
            continue
        if kind == "road":
            lcd.fill_rect(0, sy, 240, STEP, ROAD)
            lcd.fill_rect(0, sy + 2, 240, 1, SHOULDER)
            lcd.fill_rect(0, sy + 17, 240, 1, SHOULDER)
            lcd.fill_rect(0, sy, 240, 2, ROAD_EDGE)
            lcd.fill_rect(0, sy + 18, 240, 2, ROAD_EDGE)
            stripe_shift = (worldgen.mix32(world.seed ^ absolute) & 1) * 8
            for mark_x in range(0, 240, 40):
                mx = mark_x + 8 + stripe_shift
                if mx + 16 <= 240:
                    lcd.fill_rect(mx, sy + 9, 16, 2, ROAD_MARK)
            cars = generated_mask(world.seed, absolute, phase)
            for cx in range(GRID_SIZE):
                if cars & (1 << cx):
                    draw_car(lcd, cx * STEP, sy, absolute, phase, world.seed)
            continue
        mask = world.mask(absolute)
        # Sparse deterministic ground details; never affect collisions.
        for x in range(GRID_SIZE):
            if not (mask & (1 << x)):
                value = worldgen.mix32(world.seed ^ (absolute * 131) ^ (x * 7919))
                detail = value % 11
                px = x * STEP
                if detail < 3:
                    draw_flower(lcd, px, sy, (value >> 8) % 3)
                elif detail == 3:
                    lcd.fill_rect(px + 4, sy + 11, 12, 4, GRASS_PATCH)
                    lcd.fill_rect(px + 7, sy + 8, 2, 4, TREE_HIGHLIGHT)
                    lcd.fill_rect(px + 12, sy + 9, 2, 3, TREE_HIGHLIGHT)
                elif detail == 4:
                    lcd.fill_rect(px + 8, sy + 13, 5, 2, PEBBLE)
        for x in range(GRID_SIZE):
            if mask & (1 << x):
                tx = x * STEP
                variant = worldgen.mix32(world.seed ^ (absolute * 977) ^ (x * 313)) % 3
                draw_tree(lcd, tx, sy, variant)
    screen_y = (WINDOW - 1 - (row - world.first)) * STEP
    # draw_chicken accepts the stage-5 logical origin offset.
    if dead and water_frame:
        draw_splash(lcd, col * STEP, screen_y, water_frame)
    elif dead and crash_frame:
        draw_crash_star(lcd, col * STEP, screen_y, crash_frame)
    elif not dead:
        draw_chicken(lcd, MIN_X + col * STEP + chicken_dx, MIN_Y + screen_y, facing)
    # Minimal HUD. A tenth-row milestone briefly changes score color.
    if dirty_rows is None or (world.first + WINDOW - 1) in dirty_rows:
        lcd.fill_rect(0, 0, 240, 20, BG)
        score_color = CHICKEN if milestone(score) else INK
        lcd.text("SCORE %d" % score, 4, 5, score_color)
        if milestone(score):
            lcd.text("SCORE %d" % score, 5, 5, score_color)
        lcd.text("BEST %d" % best, 145, 5, INK)
    if dead:
        # The portrait is a separate scene ABOVE the popup, never inside it.
        lcd.fill_rect(72, 44, 96, 65, BG)
        draw_dead_chicken(lcd, "water" if death_kind in ("water", "offscreen") else "road",
                          crash_frame or water_frame or 5)
        lcd.fill_rect(8, 112, 224, 103, BG)
        if death_kind == "water":
            lcd.text("ALWAYS WATCH", 56, 120, INK)
            lcd.text("WHERE YOU STEP", 48, 135, INK)
        elif death_kind == "offscreen":
            lcd.text("MUST ALWAYS", 65, 120, INK)
            lcd.text("BE DECISIVE", 70, 135, INK)
        else:
            lcd.text("ALWAYS LOOK", 64, 120, INK)
            lcd.text("BEFORE YOU", 68, 134, INK)
            lcd.text("CROSS THE ROAD", 49, 148, INK)
        lcd.text("YOUR SCORE: %d" % score, 57, 173, CHICKEN)
        lcd.fill_rect(48, 193, 12, 12, color(45, 205, 80))
        lcd.text("PRESS ANY BUTTON", 65, 195, INK)
    elif paused:
        lcd.fill_rect(38, 85, 164, 72, BG)
        lcd.text("PAUSED", 96, 95, INK)
        # Colored button icons communicate physical controls without A/B jargon.
        lcd.fill_rect(54, 117, 12, 12, color(230, 45, 55))
        lcd.text("RESUME", 76, 119, INK)
        lcd.fill_rect(54, 136, 12, 12, color(45, 205, 80))
        lcd.text("NEW RUN", 76, 138, INK)
    if DEBUG:
        draw_debug_overlay(lcd, world.seed, phase)
    if dirty_rows is None or not hasattr(lcd, "show_rect"):
        lcd.show()
    else:
        # Snake's proven partial LCD transfer API. Only rows repainted
        # in the framebuffer are sent to the panel.
        for absolute in dirty_rows:
            if world.first <= absolute <= world.last:
                sy = (WINDOW - 1 - (absolute - world.first)) * STEP
                kind = terrain_kind(world.seed, absolute)
                if previous_phase is not None and kind in ("road", "logs"):
                    # Both old and new footprints must be transferred: old
                    # sprites disappear and new sprites become visible.
                    changed = (generated_mask(world.seed, absolute, previous_phase) |
                               generated_mask(world.seed, absolute, phase))
                    # Group adjacent occupied tiles to reduce SPI calls.
                    cx = 0
                    while cx < GRID_SIZE:
                        if not (changed & (1 << cx)):
                            cx += 1
                            continue
                        first = cx
                        while cx + 1 < GRID_SIZE and changed & (1 << (cx + 1)):
                            cx += 1
                        lcd.show_rect(first * STEP, sy, (cx - first + 1) * STEP, STEP)
                        cx += 1
                else:
                    lcd.show_rect(0, sy, 240, STEP)
        # The HUD overlays the uppermost terrain row.
        if (world.first + WINDOW - 1) in dirty_rows:
            lcd.show_rect(0, 0, 240, 20)
        if DEBUG:
            lcd.show_rect(0, 20, 240, 14)
    if PROFILE_RENDER:
        elapsed = time.ticks_diff(time.ticks_ms(), render_started)
        _render_frames += 1
        _render_total_ms += elapsed
        if elapsed > _render_max_ms:
            _render_max_ms = elapsed
        if _render_frames >= 30:
            debug("render avg_ms=%d max_ms=%d" % (
                _render_total_ms // _render_frames, _render_max_ms))
            _render_frames = 0
            _render_total_ms = 0
            _render_max_ms = 0

def animate_water(lcd, world, col, row, score, best, facing, phase, carried_off=False):
    """Short splash sequence, with an edge struggle before falling off."""
    for frame in range(1, 5):
        draw_world(lcd, world, col, row, score, best, False, facing,
                   dead=True, phase=phase, water_frame=frame,
                   death_kind="offscreen" if carried_off else "water")
        time.sleep_ms(90)

def animate_log_carry(lcd, world, old_col, row, score, best, facing,
                      old_phase, new_phase, keys):
    """Four visual substeps; logical collision remains grid-based."""
    if PROCEDURAL_WORLD:
        direction = worldgen.log_direction(world.seed, row)
    else:
        direction = -1 if (row // 24) & 1 else 1
    # Poll before rendering, not after: a hop off the log takes priority.
    # Do not add explicit sleeps: LCD.show() already consumes frame time.
    for step in range(1, 5):
        for pressed in keys.pressed():
            if pressed in ("up", "down", "left", "right"):
                return pressed
        draw_world(lcd, world, old_col, row, score, best, False, facing,
                   phase=old_phase if step < 3 else new_phase,
                   chicken_dx=direction * step * 5)
    return None

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
        # Fixed seed when procedural mode is disabled; timing-derived otherwise.
        seed = new_run_seed(time.ticks_ms())
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
        phase = 0
        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(score) * FRAME_MS)
        crash_animated = False
        death_kind = None
        queued_direction = None
        draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
        debug("05 world shown, seed=%d" % seed)
        while True:
            # Capture short presses before any potentially slow LCD redraw.
            # Preserve a pending log-carry direction rather than overwriting it.
            if queued_direction is None:
                early_inputs = keys.pressed()
                if early_inputs:
                    queued_direction = early_inputs[0]
            # Time-based scheduling. One cell maximum per update; a delayed
            # LCD frame cannot make cars skip several cells to catch up.
            if not paused and not dead and traffic_due(time.ticks_ms(), next_traffic_at):
                next_phase = next_traffic_phase(phase)
                if terrain_kind(seed, row) in ("logs", "lilies"):
                    if terrain_kind(seed, row) == "lilies" and not hazard_at(seed, row, col, phase):
                        pass  # Stationary pad: do not carry the chicken.
                    elif not hazard_at(seed, row, col, phase) and (not PROCEDURAL_WORLD or worldgen.log_position(seed, row, next_phase) != worldgen.log_position(seed, row, phase)):
                        carried = generated_carry(seed, row, col) if PROCEDURAL_WORLD else carry_on_log(row, col, phase)
                        if carried is None:
                            dead = True
                            death_kind = "offscreen"
                        else:
                            old_col = col
                            col = carried
                            captured = animate_log_carry(lcd, world, old_col, row, score,
                                                         best, facing, phase, next_phase, keys)
                            if queued_direction is None:
                                queued_direction = captured
                    elif hazard_at(seed, row, col, phase):
                        # Unsupported at the OLD phase: genuine water death.
                        dead = True
                        death_kind = "water"
                    # A supported stationary log/pad must not drown merely
                    # because its lane skips this traffic update.
                    if not dead and hazard_at(seed, row, col, next_phase):
                        dead = True
                        death_kind = "water"
                if not dead and terrain_kind(seed, row) == "road" and generated_traffic_hit(seed, row, col, phase, next_phase):
                    dead = True
                    crash_animated = False
                    debug("traffic collision row=%d col=%d phase=%d" %
                          (row, col, next_phase))
                phase = next_phase
                if dead:
                    if death_kind in ("water", "offscreen"):
                        animate_water(lcd, world, col, row, score, best, facing, phase,
                                      death_kind == "offscreen")
                    else:
                        animate_crash(lcd, world, col, row, score, best, facing, phase)
                    crash_animated = True
                else:
                    if PROCEDURAL_WORLD and queued_direction is None:
                        captured = preview_traffic(lcd, world, phase - 1, phase, row, keys)
                        if captured is not None:
                            queued_direction = captured
                    draw_world(lcd, world, col, row, score, best, paused, facing,
                               dead=False, phase=phase,
                               dirty_rows=changed_hazard_rows(world, phase - 1, phase, row),
                               previous_phase=phase - 1)
                next_traffic_at = time.ticks_add(
                    time.ticks_ms(), traffic_interval(score) * FRAME_MS)
            if queued_direction is not None:
                inputs = (queued_direction,)
                queued_direction = None
            else:
                inputs = keys.pressed()
            for key in inputs:
                if dead:
                    if key in ("A", "B", "Y", "up", "down", "left", "right"):
                        seed = new_run_seed(time.ticks_ms())
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        phase = 0
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(0) * FRAME_MS)
                        facing = "down"
                        dead = False
                        crash_animated = False
                        death_kind = None
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
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(score) * FRAME_MS)
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
                        phase = 0
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(0) * FRAME_MS)
                        facing = "right"
                        paused = False
                        death_kind = None
                        debug("new run")
                        draw_world(lcd, world, col, row, score, best, paused, facing)
                    break
                if key in ("up", "down", "left", "right"):
                    if PROCEDURAL_WORLD:
                        nc, nr, _ = generated_move(world, col, row, key, phase)
                    else:
                        nc, nr = move_world(world, col, row, key)
                    if (nc, nr) != (col, row):
                        col, row = nc, nr
                        facing = key
                        death_kind = None
                        if terrain_kind(seed, row) in ("logs", "lilies") and hazard_at(seed, row, col, phase):
                            dead = True
                            death_kind = "water"
                        else:
                            dead = terrain_kind(seed, row) == "road" and hazard_at(seed, row, col, phase)
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
                            if death_kind == "water":
                                animate_water(lcd, world, col, row, score, best, facing, phase)
                            else:
                                animate_crash(lcd, world, col, row, score, best, facing, phase)
                            crash_animated = True
                        else:
                            draw_world(lcd, world, col, row, score, best, paused, facing, dead=dead, phase=phase,
                                   death_kind=death_kind)
                    else:
                        debug("blocked %s row=%d col=%d" % (key, row, col))
                    break
            time.sleep_ms(10)  # Input poll cadence; traffic still uses FRAME_MS.
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
