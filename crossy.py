"""Wedgie Crossy: first grass-only playable MicroPython cartridge."""
import time
from lcd import LCD, Keys, color
import save

lcd = LCD()
keys = Keys()
TILE = 20
BOARD_Y = 20
ROWS = 11
COLS = 12
FRAME_MS = 45
GRASS = color(58, 130, 64)
ALT = color(48, 112, 55)
TREE = color(20, 75, 38)
CHICKEN = color(255, 230, 90)
INK = color(245, 245, 230)
BG = color(12, 20, 15)

seed = 1
player_x = 5
player_y = 0
best_row = 0
score = 0
best = 0
dead = False
last_progress = 0
boundary = -3
rows = [0] * ROWS

def random_below(n):
    global seed
    seed ^= (seed << 13) & 0xffffffff
    seed ^= seed >> 17
    seed ^= (seed << 5) & 0xffffffff
    seed &= 0xffffffff
    return seed % n

def tree_mask(index):
    # No tree is placed in the guaranteed central corridor.
    if index < 2:
        return 0
    mask = 0
    for x in range(COLS):
        if x != 5 and random_below(7) == 0:
            mask |= 1 << x
    return mask

def reset():
    global seed, player_x, player_y, best_row, score, dead
    global last_progress, boundary
    try:
        from wedgie import rand_below
        seed = rand_below(0x7fffffff) + 1
    except (ImportError, AttributeError, ValueError):
        seed = (time.ticks_ms() | 1) & 0xffffffff
    player_x, player_y, best_row, score = 5, 0, 0, 0
    dead, last_progress, boundary = False, time.ticks_ms(), -3
    for i in range(ROWS):
        rows[i] = tree_mask(i)

def mask_at(index):
    if index < 0 or index < best_row - ROWS + 1:
        return None
    if index >= best_row + ROWS:
        return None
    return rows[index % ROWS]

def move(direction):
    global player_x, player_y, best_row, score, last_progress
    dx, dy = 0, 0
    if direction == "up": dy = 1
    elif direction == "down": dy = -1
    elif direction == "left": dx = -1
    elif direction == "right": dx = 1
    else: return
    x, y = player_x + dx, player_y + dy
    if x < 0 or x >= COLS or y < 0:
        return
    if y > best_row:
        # Append one new row before crossing it.
        rows[y % ROWS] = tree_mask(y)
    mask = mask_at(y)
    if mask is None or (mask & (1 << x)):
        return
    player_x, player_y = x, y
    if y > best_row:
        best_row = y
        score = best_row
        last_progress = time.ticks_ms()

def update_camera(now):
    global boundary, dead
    elapsed = time.ticks_diff(now, last_progress)
    if elapsed > 5000:
        candidate = -3 + 1 + (elapsed - 5001) // 1000
        if candidate > boundary:
            boundary = candidate
    if player_y <= boundary:
        dead = True

def draw():
    lcd.fill(BG)
    lcd.text("CROSSY %d" % score, 4, 4, INK)
    lcd.text("BEST %d" % best, 135, 4, INK)
    first = best_row - ROWS + 1
    for screen_row in range(ROWS):
        world_row = first + screen_row
        if world_row < 0:
            continue
        y = BOARD_Y + (ROWS - 1 - screen_row) * TILE
        lcd.fill_rect(0, y, 240, TILE, GRASS if world_row & 1 else ALT)
        mask = mask_at(world_row)
        if mask is not None:
            for x in range(COLS):
                if mask & (1 << x):
                    lcd.fill_rect(x * TILE + 3, y + 3, 14, 14, TREE)
        if world_row == player_y:
            lcd.fill_rect(player_x * TILE + 4, y + 4, 12, 12, CHICKEN)
    if dead:
        lcd.fill_rect(24, 90, 192, 52, BG)
        lcd.text("GAME OVER", 70, 101, INK)
        lcd.text("A TO RESTART", 65, 120, INK)
    lcd.show()

def run():
    global best
    try:
        best = save.load("best", 0)
    except OSError:
        best = 0
    reset()
    while True:
        now = time.ticks_ms()
        presses = keys.pressed()
        if dead:
            if "A" in presses or "press" in presses:
                reset()
        else:
            for direction in ("up", "down", "left", "right"):
                if direction in presses:
                    move(direction)
                    break
            update_camera(now)
            if dead and score > best:
                best = score
                try:
                    save.store("best", best)
                except OSError:
                    pass
        draw()
        remaining = FRAME_MS - time.ticks_diff(time.ticks_ms(), now)
        if remaining > 0:
            time.sleep_ms(remaining)
        else:
            time.sleep_ms(1)
