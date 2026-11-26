"""Crossy runtime, imported only when the game is launched.

Splitting the entry loop keeps the initial crossy module smaller and avoids
compiling the full event loop during the initial module import.
"""
from crossy import *
from crossy import _render_frames, _render_total_ms, _render_max_ms

def run():
    import save  # Firmware-only module; host logic tests can import crossy without it.
    if gc is not None:
        gc.collect()
        if hasattr(gc, "mem_free"):
            debug("heap before LCD=%d" % gc.mem_free())
    debug("01 run entered")
    lcd = None
    try:
        debug("02 creating LCD")
        lcd = LCD()
        if gc is not None:
            gc.collect()
            if hasattr(gc, "mem_free"):
                debug("heap after LCD=%d" % gc.mem_free())
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
        title_screen(lcd, keys, best)
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
        last_smooth_at = time.ticks_ms()
        last_smooth_step = -1
        draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
        progress_at = time.ticks_ms()
        pressure_applied = 0
        paused_at = progress_at
        debug("05 world shown, seed=%d" % seed)
        while True:
            # Capture short presses before any potentially slow LCD redraw.
            # Preserve a pending log-carry direction rather than overwriting it.
            if dead and not DEV_MODE and best > saved_best:
                try:
                    save.store("best", best)
                    saved_best = best
                except OSError as exc:
                    debug("best save failed: %r" % (exc,))
            if queued_direction is None:
                early_inputs = keys.pressed()
                if early_inputs:
                    queued_direction = early_inputs[0]
            if not paused and not dead:
                now = time.ticks_ms()
                elapsed = time.ticks_diff(now, progress_at)
                warning = elapsed >= 5000 and (elapsed // 250) % 2 == 0
                due = pressure_rows(elapsed)
                if due > pressure_applied:
                    target = world.first + due - pressure_applied
                    pressure_applied = due
                    if target > row:
                        dead = True
                        death_kind = "eagle"
                        animate_eagle(lcd, world, col, row, score, best, facing, phase)
                        crash_animated = True
                        queued_direction = None
                        continue
                    world.advance(target)
                    world.pressure_warning = warning
                    draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
                elif warning != world.pressure_warning:
                    world.pressure_warning = warning
                    draw_world(lcd, world, col, row, score, best, paused, facing,
                               phase=phase, dirty_rows=[world.first])
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
                            # Avoid four blocking full-screen flushes while
                            # crossing logs. The next normal draw shows the
                            # carried position; keep joystick polling live.
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
                if not dead and terrain_kind(seed, row) == "rail" and generated_traffic_hit(seed, row, col, phase, next_phase):
                    dead = True
                    death_kind = "rail"
                    crash_animated = False
                phase = next_phase
                if dead:
                    if death_kind in ("water", "offscreen"):
                        animate_water(lcd, world, col, row, score, best, facing, phase,
                                      death_kind == "offscreen")
                    elif death_kind == "rail":
                        animate_train_crash(lcd, world, col, row, score, best, facing, phase)
                    else:
                        animate_crash(lcd, world, col, row, score, best, facing, phase)
                    crash_animated = True
                else:
                    # Never replay old traffic phase after the tick.
                    draw_world(lcd, world, col, row, score, best, paused, facing,
                               dead=False, phase=phase,
                               dirty_rows=changed_hazard_rows(world, phase - 1, phase, row),
                               previous_phase=phase - 1)
                next_traffic_at = time.ticks_add(
                    time.ticks_ms(), traffic_interval(score) * FRAME_MS)
                last_smooth_step = -1
                last_smooth_at = time.ticks_ms()
            # Render between simulation ticks, never delaying a due tick.
            # A slow LCD simply reduces cosmetic FPS, not input cadence.
            if not paused and not dead and queued_direction is None and SMOOTH_TRAFFIC:
                now = time.ticks_ms()
                interval_ms = traffic_interval(score) * FRAME_MS
                remaining = time.ticks_diff(next_traffic_at, now)
                elapsed = interval_ms - remaining
                step = pixel_offset(elapsed, interval_ms, STEP)
                if (0 < step < STEP and step != last_smooth_step
                        and time.ticks_diff(now, last_smooth_at) >= SMOOTH_FRAME_MS
                        and remaining > SMOOTH_FRAME_MS):
                    # Use the same world renderer as joystick redraws.
                    # Two independent car renderers caused phase disagreement.
                    road_rows = []
                    for ri in range(WINDOW - 1):
                        ar = world.first + ri
                        if (ar != row and terrain_kind(world.seed, ar) == "road") or (terrain_kind(world.seed, ar) == "rail" and worldgen.train_stage(seed, ar, phase) == 2):
                            road_rows.append(ar)
                    if road_rows:
                        draw_world(lcd, world, col, row, score, best, paused,
                                   facing, phase=phase, dirty_rows=road_rows,
                                   road_step=step)
                    last_smooth_at = time.ticks_ms()
                    last_smooth_step = step
            if queued_direction is not None:
                inputs = (queued_direction,)
                queued_direction = None
            else:
                inputs = keys.pressed()
            for key in inputs:
                if dead:
                    if key:
                        seed = new_run_seed(time.ticks_ms())
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        phase = 0
                        progress_at = time.ticks_ms()
                        pressure_applied = 0
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(0) * FRAME_MS)
                        facing = "down"
                        dead = False
                        crash_animated = False
                        death_kind = None
                        draw_world(lcd, world, col, row, score, best, False, facing, phase=phase)
                    break
                if key == "Y" and not paused:
                    paused = True
                    paused_at = time.ticks_ms()
                    debug("paused")
                    draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
                    break
                if paused:
                    if key in ("B", "Y"):
                        paused = False
                        progress_at = time.ticks_add(progress_at, time.ticks_diff(time.ticks_ms(), paused_at))
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(score) * FRAME_MS)
                        debug("resumed")
                        draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
                    elif key == "A":
                        if not DEV_MODE and best > saved_best:
                            try:
                                save.store("best", best)
                                saved_best = best
                            except OSError as exc:
                                debug("best save failed: %r" % (exc,))
                        world = World(seed)
                        col, row, score = START_COL, START_ROW, 0
                        phase = 0
                        progress_at = time.ticks_ms()
                        pressure_applied = 0
                        next_traffic_at = time.ticks_add(time.ticks_ms(), traffic_interval(0) * FRAME_MS)
                        facing = "right"
                        paused = False
                        death_kind = None
                        debug("new run")
                        draw_world(lcd, world, col, row, score, best, paused, facing, phase=phase)
                    break
                if key in ("up", "down", "left", "right"):
                    if PROCEDURAL_WORLD:
                        nc, nr, _ = generated_move(world, col, row, key, phase)
                    else:
                        nc, nr = move_world(world, col, row, key)
                    if (nc, nr) != (col, row):
                        old_row = row
                        old_first = world.first
                        old_score = score
                        col, row = nc, nr
                        facing = key
                        death_kind = None
                        if terrain_kind(seed, row) in ("logs", "lilies") and hazard_at(seed, row, col, phase):
                            dead = True
                            death_kind = "water"
                        else:
                            dead = terrain_kind(seed, row) in ("road", "rail") and hazard_at(seed, row, col, phase)
                            if dead and terrain_kind(seed, row) == "rail":
                                death_kind = "rail"
                        if dead:
                            crash_animated = False
                        if row > score:
                            score = row
                            progress_at = time.ticks_ms()
                            pressure_applied = 0
                            if world.pressure_warning:
                                world.pressure_warning = False
                                old_first = -1  # clear warning with full redraw
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
                            elif death_kind == "rail":
                                animate_train_crash(lcd, world, col, row, score, best, facing, phase)
                            else:
                                animate_crash(lcd, world, col, row, score, best, facing, phase)
                            crash_animated = True
                        else:
                            now = time.ticks_ms()
                            interval_ms = traffic_interval(score) * FRAME_MS
                            remaining = time.ticks_diff(next_traffic_at, now)
                            road_step = pixel_offset(interval_ms - remaining, interval_ms, STEP)
                            # Ordinary hops change at most two terrain rows.
                            # Preserve the framebuffer and transfer only those
                            # strips; scrolling still needs a full redraw.
                            dirty = None
                            if world.first == old_first:
                                dirty = [old_row]
                                if row != old_row:
                                    dirty.append(row)
                                if score != old_score:
                                    dirty.append(world.first + WINDOW - 1)
                            draw_world(lcd, world, col, row, score, best, paused, facing,
                                       dead=dead, phase=phase, death_kind=death_kind,
                                       road_step=road_step, dirty_rows=dirty)
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
