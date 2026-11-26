"""Death portraits; imported only when needed."""
from lcd import color

INK = color(245, 245, 230)
CHICKEN = color(255, 215, 70)
BEAK = color(245, 120, 40)
EYE = color(18, 25, 20)
TREE_TRUNK = color(105, 64, 28)
ROAD_EDGE = color(135, 140, 135)
CAR_BLUE = color(55, 125, 220)
CAR_YELLOW = color(235, 170, 45)
CAR = color(210, 55, 45)
CAR_WINDOW = color(125, 190, 205)
CAR_WHEEL = color(25, 30, 35)
WATER = color(35, 105, 175)
SPLASH = color(215, 240, 255)
LOG = color(130, 83, 42)
LOG_DARK = color(88, 53, 30)
LOG_HIGHLIGHT = color(185, 132, 76)
WATER_RIPPLE = color(65, 135, 195)

def draw_special_death(lcd, kind, frame, direction=1):
    """Clipped portrait animation; never paint over score or restart text."""
    # Reuse the lane clip for vertical bounds; explicitly clip horizontal
    # coordinates to the portrait, not merely the physical screen.
    def rect(x, y, w, h, ink):
        left, right = max(72, x), min(168, x+w)
        top, bottom = max(44, y), min(109, y+h)
        if left < right and top < bottom:
            lcd.fill_rect(left, top, right-left, bottom-top, ink)
    frame = max(1, min(5, frame))
    if kind == "eagle":
        # Dive, spread wings, grab, then climb out of the portrait.
        cy = (43, 55, 69, 48, 24)[frame-1]
        cx = (94, 108, 120, 132, 145)[frame-1]
        brown = color(112, 67, 35)
        feather = color(172, 115, 62)
        white = color(250, 244, 220)
        for side in (-1, 1):
            for i in range(5):
                wx = cx + side*(10+i*6)
                wy = cy - i*3 if frame in (1, 4, 5) else cy+i*2
                rect(wx-4, wy, 9, 12-i, LOG_DARK)
                rect(wx-3, wy+1, 6, 5, feather)
            rect(cx+side*10-5, cy+5, 10, 10, brown)
        rect(cx-9, cy, 18, 20, brown)
        rect(cx-6, cy+15, 12, 10, LOG_DARK)
        rect(cx-6, cy-5, 15, 12, white)
        rect(cx+5, cy, 8, 5, BEAK)
        rect(cx+3, cy-2, 2, 2, EYE)
        for dx in (-6, 5):
            rect(cx+dx, cy+21, 3, 7, BEAK)
            rect(cx+dx-2, cy+26, 7, 2, BEAK)
        # Rounded chicken body, feathered wing, comb, eye and feet.
        px = 120 if frame < 3 else cx
        py = 87 if frame < 3 else cy+28
        rect(px-11, py, 22, 10, CHICKEN)
        rect(px-8, py-3, 16, 16, CHICKEN)
        rect(px-15, py-5, 8, 7, CHICKEN)
        rect(px+3, py-9, 11, 12, CHICKEN)
        rect(px+5, py-12, 3, 5, CAR)
        rect(px+9, py-13, 3, 6, CAR)
        rect(px+13, py-4, 6, 4, BEAK)
        rect(px+10, py-6, 2, 2, EYE)
        rect(px-6, py+2, 10, 5, CAR_YELLOW)
        for dx in (-5, 5):
            rect(px+dx, py+12, 2, 5, BEAK)
            rect(px+dx, py+16, 5, 2, BEAK)
        if frame in (2, 3):
            for dx, dy in ((-26,-8),(24,-12),(-20,12),(27,9)):
                rect(px+dx, py+dy, 4, 2, INK)
    elif kind == "rail":
        rect(72, 92, 96, 17, ROAD_EDGE)
        for x in range(72, 168, 12):
            rect(x, 93, 5, 16, TREE_TRUNK)
        rect(72, 96, 96, 3, INK)
        rect(72, 105, 96, 3, INK)
        h = max(3, 24-frame*5)
        rect(104-frame*2, 96-h, 32+frame*4, h, CHICKEN)
        rect(132+frame*2, 94, 7, 3, BEAK)
        front = 92+frame*16
        for x in (front-100, front-50):
            rect(x, 62, 46, 29, CAR_BLUE)
            rect(x+5, 67, 14, 10, CAR_WINDOW)
            rect(x+25, 67, 14, 10, CAR_WINDOW)
            for wheel in (x+5, x+29):
                rect(wheel, 87, 12, 12, CAR_WHEEL)
        rect(front, 62, 42, 29, CAR)
        rect(front+4, 51, 23, 15, CAR)
        rect(front+8, 55, 15, 9, CAR_WINDOW)
        rect(front+30, 68, 12, 5, CAR_YELLOW)
        for wheel in (front+4, front+26):
            rect(wheel, 87, 12, 12, CAR_WHEEL)
    else:
        rect(72, 44, 96, 65, WATER)
        for x in range(76, 168, 20):
            rect(x, 56, 10, 2, WATER_RIPPLE)
            rect(x-5, 99, 12, 2, WATER_RIPPLE)
        center = 120 + direction*(frame-1)*18
        rect(center-28, 83, 56, 14, LOG_DARK)
        rect(center-26, 84, 52, 11, LOG)
        rect(center-23, 85, 46, 2, LOG_HIGHLIGHT)
        rect(center-10, 66, 20, 17, CHICKEN)
        rect(center-5, 60, 13, 12, CHICKEN)
        rect(center+direction*9-3, 68, 6, 4, BEAK)
        rect(center+direction*4, 63, 2, 2, EYE)

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

